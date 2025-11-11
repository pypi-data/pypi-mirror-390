import subprocess
import logging

from typing import Optional


def run_plink2(command: str):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        check=False
    )
    if result.returncode != 0:
        logging.debug("Error: %s", result.stderr)
    else:
        logging.debug("Output: %s", result.stdout)


def create_sorted_pgen(
    plink2_path: str,
    ped_file: str,
    map_file: str,
    output_prefix: str
) -> None:
    cmd = f"{plink2_path} --ped {ped_file} --map {map_file} --make-pgen --sort-vars --out {output_prefix}_temp"
    run_plink2(cmd)


def generate_bed_bim_fam(
    plink2_path: str,
    ped_file: str,
    map_file: str,
    output_prefix: str,
    relax_mind_threshold: bool = False,
    maf_threshold: float = 0.05,
    sample_keep_path: Optional[str] = None,
    autosomes_only: bool = True,
):
    """
    Generates BED/BIM/FAM from PED/MAP using PLINK2.

    NOTE:
        # NEW: default to legacy-like MAF≥0.05

    Args:
        plink2_path: Path to PLINK2.
        ped_file: PED path.
        map_file: MAP path.
        output_prefix: Output prefix (no extension).
        relax_mind_threshold: If True, skip per-sample missingness filter.
        maf_threshold: Minor allele frequency filter for SNPs (e.g., 0.05).
        sample_keep_path: Path to file with samples to keep.
        autosomes_only: If True, restrict to autosomal chromosomes only.
    """

    mind = "" if relax_mind_threshold else "--mind 0.1"
    maf  = f"--maf {maf_threshold}" if maf_threshold is not None else ""
    keep = f"--keep {sample_keep_path}" if sample_keep_path else ""
    chrflag = "--chr 1-19" if autosomes_only else "" # mouse autosomes

    logging.info("[plink_utils:generate_bed_bim_fam] Creating sorted pgen.")
    create_sorted_pgen(plink2_path, ped_file, map_file, output_prefix)

    logging.info("[plink_utils:generate_bed_bim_fam] Converting to BED (geno 0.1) with %s %s %s %s",
                 mind or "no --mind", maf or "no --maf", keep or "no --keep", chrflag or "all chr")
    run_plink2(
        f"{plink2_path} --pfile {output_prefix}_temp --make-bed "
        f"--geno 0.1 {mind} {maf} {keep} {chrflag} --out {output_prefix}"
    )


def generate_bed_bim_fam_V0(
    plink2_path: str,
    ped_file: str,
    map_file: str,
    output_prefix: str,
    relax_mind_threshold: bool = False,
    mind_threshold: float = 0.1,
    maf_threshold: float = 0.05,
    sample_keep_path: Optional[str] = None
):
    """
    Generates BED/BIM/FAM from PED/MAP using PLINK2.

    NOTE:
        # NEW: default to legacy-like MAF≥0.05

    Args:
        plink2_path: Path to PLINK2.
        ped_file: PED path.
        map_file: MAP path.
        output_prefix: Output prefix (no extension).
        relax_mind_threshold: If True, skip per-sample missingness filter.
        maf_threshold: Minor allele frequency filter for SNPs (e.g., 0.05).
    """
    mind = "" if relax_mind_threshold else f"--mind {mind_threshold}"
    maf  = f"--maf {maf_threshold}" if maf_threshold is not None else ""
    keep = f"--keep {sample_keep_path}" if sample_keep_path else ""

    logging.info("[plink_utils:generate_bed_bim_fam] Creating sorted pgen.")
    create_sorted_pgen(plink2_path, ped_file, map_file, output_prefix)

    logging.info(
        "[plink_utils:generate_bed_bim_fam] Converting to BED with mind: %s, maf: %s, keep: %s",
        mind or "None", maf or "None", keep or "None"
    )
    run_plink2(
        f"{plink2_path} --pfile {output_prefix}_temp --make-bed "
        f"--geno 0.1 {mind} {maf} {keep} --out {output_prefix}"
    )


def calculate_kinship_matrix(
    plink2_path: str,
    input_prefix: str,
    output_prefix: str,
    sample_keep_path: Optional[str] = None
):
    """
    Create PLINK .kin files from BED/BIM/FAM files.
    """
    keep = f"--keep {sample_keep_path}" if sample_keep_path else ""
    cmd = f"{plink2_path} --bfile {input_prefix} {keep} --make-rel square --out {output_prefix}"
    run_plink2(cmd)
