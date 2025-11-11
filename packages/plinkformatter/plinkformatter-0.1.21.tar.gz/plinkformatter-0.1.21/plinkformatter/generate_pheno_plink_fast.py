"""
Faster + lower-RAM replacements for PLINK file generation
"""
from __future__ import annotations
import os
import io
import math
from collections import defaultdict
from typing import Dict, Iterable, List, Tuple, Optional
from pathlib import Path

import numpy as np
import pandas as pd


from plinkformatter.plink_utils import generate_bed_bim_fam, calculate_kinship_matrix
from plinkformatter.generate_pheno_plink import extract_pheno_measure
# ----------------------------
# Helpers: normalization & IO
# ----------------------------


def _sanitize_strain(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    return s.replace("?", "").replace(" ", "").upper()


def _base_id(mid) -> str:
    s = str(mid)
    return s.split("_", 1)[0]


def _read_map_sanitized(map_file: str) -> pd.DataFrame:
    """Read MAP and apply the same rs sanitization as your code.
    If rs==".", replace with f"chr_bp".
    """
    df = pd.read_csv(map_file, header=None, sep="\t")
    # columns: 0=chr, 1=rs, 2=cM, 3=bp38
    df[1] = np.where(df[1] == ".", df[0].astype(str) + "_" + df[3].astype(str), df[1].astype(str))
    return df


def _iter_ped_strain_offsets(ped_path: str) -> Dict[str, int]:
    """Single pass to collect byte offsets for each strain (FID) without storing lines.
    Returns { sanitized_FID: offset }.
    Assumes unique strain rows.
    """
    offsets: Dict[str, int] = {}
    with open(ped_path, "rb") as f:
        while True:
            pos = f.tell()
            line = f.readline()
            if not line:
                break
            # PED file appears TAB-delimited between fields; genotype pairs are within-field "A B".
            first_tab = line.find(b"\t")
            fid_bytes = (line.strip().split()[0] if first_tab <= 0 else line[:first_tab])
            name = _sanitize_strain(fid_bytes.decode(errors="replace"))
            if name and name not in offsets:
                offsets[name] = pos
    return offsets


def _read_ped_line_at_offset(ped_path: str, offset: int) -> str:
    with open(ped_path, "rb") as f:
        f.seek(offset)
        raw = f.readline()
    return raw.decode(errors="replace").rstrip("\n")


def _parse_tab_ped_line_to_parts(line: str) -> List[str]:
    """Split a TAB-delimited PED line into fields.
    Note: genotype pairs remain as one field each, like "2 2", "1 2".
    """
    parts = line.split("\t")
    if len(parts) <= 6:  # guard for space-delimited inputs
        parts = line.split()
    return parts


def _flatten_pairs_to_space_stream(parts: List[str], sex_flag: str, phe_value: Optional[float]) -> str:
    """Create a space-delimited PED record from TAB parts, updating SEX and PHE (col6).
    SEX: 2 for 'f', 1 for 'm'. PHE: zscore (None -> keep original).
    """
    if len(parts) < 7:
        raise ValueError("Malformed PED: expected >=7 columns (6 meta + genotypes)")

    meta = parts[:6]
    meta[4] = "2" if sex_flag == "f" else "1"
    if phe_value is not None:
        meta[5] = "-9" if (isinstance(phe_value, float) and math.isnan(phe_value)) else (str(phe_value))

    out = io.StringIO()
    out.write(" ".join(meta))
    for gp in parts[6:]:
        a_b = gp.split(" ")
        if len(a_b) != 2:
            a_b = gp.split()
            if len(a_b) != 2:
                raise ValueError(f"Genotype pair not splitable into two alleles: {gp!r}")
        out.write(f" {a_b[0]} {a_b[1]}")
    return out.getvalue()


def write_keep_ids(pheno_path: str, fam_path: Optional[str], out_path: str) -> int:
    """
    Build a PLINK --keep file (two columns: FID IID, no header) for samples with
    non-NaN phenotype. If fam_path is provided, intersect with FAM; otherwise
    just emit from PHENO.
    """
    ph = pd.read_csv(pheno_path, sep=r"\s+", header=None, usecols=[0,1,2],
                 names=["FID","IID","zscore"], engine="python")
    vals = pd.to_numeric(ph["zscore"], errors="coerce")
    mask = vals.notna() & (vals != -9)
    ph = ph[mask][["FID", "IID"]]

    if fam_path:
        fam = pd.read_csv(fam_path, sep=r"\s+", header=None, usecols=[0,1],
                          names=["FID","IID"], engine="python")
        keep = ph.merge(fam, on=["FID","IID"], how="inner")[["FID","IID"]]
    else:
        keep = ph

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    keep.to_csv(out_path, sep=" ", header=False, index=False)
    return len(keep)


# ----------------------------
# Core: fast generator
# ----------------------------
def generate_pheno_plink_fast(
    ped_file: str,
    map_file: str,
    pheno: pd.DataFrame,
    outdir: str,
    ncore: int = 1,
) -> pd.DataFrame:
    """
    Streaming, memory-safe replacement for generate_pheno_plink.

    Matches original semantics:
      - normalize strains, keep only f/m
      - filter strains by PED presence
      - stable sort by strain
      - replicate PED row per pheno row
      - set PED col5 (SEX) = 2 for 'f', 1 for 'm'
      - set PED col6 (PHE) = zscore
      - write .pheno with: FID IID zscore value

    Returns the filtered+sorted pheno (pheno_s) for parity with your API.
    """
    os.makedirs(outdir, exist_ok=True)

    # Validate / normalize pheno
    if pheno is None or pheno.empty:
        return pd.DataFrame()
    for col in ("strain", "sex", "measnum"):
        if col not in pheno.columns:
            raise ValueError("pheno must have columns: 'strain', 'sex', 'measnum' (plus 'zscore'/'value')")

    ph = pheno.copy()
    ph["strain"] = ph["strain"].astype(str).str.replace(" ", "", regex=False).str.upper()
    ph = ph[ph["sex"].isin(["f", "m"])].copy()
    if ph.empty:
        return ph

    # Index PED by strain (byte offsets)
    ped_index = _iter_ped_strain_offsets(ped_file)
    ped_strains = set(ped_index.keys())

    # Filter pheno to strains present in PED, stable sort by strain
    ph = ph[ph["strain"].isin(ped_strains)].sort_values(by="strain", kind="stable").reset_index(drop=True)
    if ph.empty:
        return ph

    # Load and sanitize MAP once, copy per group
    map_df = _read_map_sanitized(map_file)

    # Group by measnum/sex (preserve overall order)
    groups: Dict[Tuple[int, str], pd.DataFrame] = {}
    for (measnum, sex), df in ph.groupby(["measnum", "sex"], sort=False):
        groups[(int(measnum), str(sex))] = df

    for (measnum, sex), df in groups.items():
        # Write MAP
        map_out = os.path.join(outdir, f"{measnum}.{sex}.map")
        map_df.to_csv(map_out, sep="\t", index=False, header=False)

        # Build per-strain queues (zscore,value) in this group's order
        # Need to make IID unique per animal_id to avoid duplicate id errors in PLINK.
        queues: Dict[str, List[Tuple[str, Optional[float], Optional[float]]]] = defaultdict(list)
        for row in df.itertuples(index=False):
            strain = str(row.strain)
            aid = getattr(row, "animal_id", None)
            if aid is None or (isinstance(aid, float) and math.isnan(aid)):
                # fallback to a stable per-strain counter when animal_id is missing
                aid = f"rep{len(queues[strain]) + 1}"
            aid_str = str(aid).replace(" ", "_").replace("/", "-")
            queues[strain].append((aid_str, getattr(row, "zscore", np.nan), getattr(row, "value", np.nan)))

        unique_strains = list(dict.fromkeys(df["strain"].tolist()))  # preserves order

        ped_out = os.path.join(outdir, f"{measnum}.{sex}.ped")
        pheno_out = os.path.join(outdir, f"{measnum}.{sex}.pheno")

        with open(ped_out, "w", encoding="utf-8") as f_ped, open(pheno_out, "w", encoding="utf-8") as f_ph:
            for strain in unique_strains:
                off = ped_index.get(strain)
                if off is None:
                    continue
                line = _read_ped_line_at_offset(ped_file, off)
                parts = _parse_tab_ped_line_to_parts(line)
                if len(parts) >= 2:
                    parts[0] = _sanitize_strain(parts[0])  # FID (strain)
                    parts[1] = _sanitize_strain(parts[1])  # IID (will be overridden per animal)

                for aid, z, v in queues[strain]:
                    # --- make IID unique per animal while keeping FID=strain ---
                    iid_unique = f"{strain}__{aid}"
                    parts_mod = list(parts)
                    parts_mod[1] = iid_unique

                    # PED: set SEX & PHE=zscore
                    space_line = _flatten_pairs_to_space_stream(parts_mod, sex_flag=sex, phe_value=z)
                    f_ped.write(space_line + "\n")

                    # PHENO: FID IID zscore  (no header; PyLMM treats -9/NA as missing)
                    z_num = None
                    if z is not None:
                        try:
                            z_num = float(z)
                        except Exception:
                            z_num = None

                    if z_num is None or not math.isfinite(z_num):
                        z_out = "-9"
                    else:
                        # compact numeric with no "nan"/"inf" strings
                        z_out = f"{z_num:.6g}"

                    f_ph.write(f"{strain} {iid_unique} {z_out}\n")

    return ph


# ------------------------------------------------------------------
# Fast end-to-end prepare (writes BED/BIM/FAM + KIN like your app)
# ------------------------------------------------------------------
def fast_prepare_pylmm_inputs(
    ped_file: str,
    map_file: str,
    measure_id_directory: str,
    measure_ids: List,
    outdir: str,
    ncore: int,
    plink2_path: str,
    *,
    ped_pheno_field: str = "zscore",  # accepted for API compatibility; ignored (we always write zscore to PED col6)
) -> None:
    """
    Fast replacement for prepare_pylmm_inputs that uses the streaming PED writer
    but produces the *same set of downstream PLINK outputs* as your current pipeline:
      - {base_id}.{sex}.ped/.map/.pheno
      - {base_id}.{sex}.bed/.bim/.fam
      - {base_id}.{sex}.kin.rel and .rel.id

    - base_id follows your current logic: split on first underscore (e.g., "131063_BXD" -> "131063").
    - Only runs PLINK for sexes that have corresponding .ped files.

    ped_pheno_field is accepted for compatibility but ignored (this function always writes zscore to PED col6).
    """
    os.makedirs(outdir, exist_ok=True)

    # 1) Extract phenotype using the measure_ids AS GIVEN (e.g., "131063_BXD" -> read 131063_BXD.csv)
    pheno = extract_pheno_measure(measure_id_directory, measure_ids)

    if pheno is None or pheno.empty:
        return

    # 2) Generate .ped/.map/.pheno with streaming (same semantics; PED col6=zscore)
    generate_pheno_plink_fast(
        ped_file=ped_file,
        map_file=map_file,
        pheno=pheno,
        outdir=outdir,
        ncore=ncore,
    )

    # 3) For each requested measure (original ids), derive base_id and produce BED/BIM/FAM + KIN
    for measure_id in measure_ids:
        base_id = _base_id(measure_id)
        for sex in ("f", "m"):
            ped_path  = os.path.join(outdir, f"{base_id}.{sex}.ped")
            map_path  = os.path.join(outdir, f"{base_id}.{sex}.map")
            pheno_path = os.path.join(outdir, f"{base_id}.{sex}.pheno")
            out_prefix = os.path.join(outdir, f"{base_id}.{sex}")

            if not os.path.exists(ped_path):
                continue

            # 1) Build keep file from PHENO (non-missing 'value'); FAM not created yet
            keep_path = f"{out_prefix}.keep.id"
            n_kept = write_keep_ids(pheno_path, fam_path=None, out_path=keep_path)

            # 2) Create BED/BIM/FAM with --keep (restricts cohort at BED stage)
            generate_bed_bim_fam(
                plink2_path=plink2_path,
                ped_file=ped_path,
                map_file=map_path,
                output_prefix=out_prefix,
                relax_mind_threshold=False,
                maf_threshold=0.05,
                sample_keep_path=keep_path,
                autosomes_only=True
            )

            # 3) Kinship matrix on the same cohort (redundant but safe)
            kin_prefix = os.path.join(outdir, f"{base_id}.{sex}.kin")
            calculate_kinship_matrix(
                plink2_path=plink2_path,
                input_prefix=out_prefix,
                output_prefix=kin_prefix,
                sample_keep_path=keep_path
            )



__all__ = [
    "generate_pheno_plink_fast",
    "fast_prepare_pylmm_inputs",
]
