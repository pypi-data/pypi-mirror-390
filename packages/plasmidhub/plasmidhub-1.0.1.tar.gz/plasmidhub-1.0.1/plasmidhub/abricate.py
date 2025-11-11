"""
Run Abricate in bulk mode on multiple FASTA files for multiple databases.

This script scans a directory for plasmid FASTA files and runs Abricate against 
a specified list of databases. Results for each database are saved separately 
in the provided results directory.

Parameters:
    input_dir (str): Path to the directory containing plasmid FASTA files (.fna, .fa, .fasta).
    results_dir (str): Directory where Abricate results will be stored.
    db_list (list): List of Abricate database names to use for screening.
    threads (int, optional): Number of CPU threads to use for Abricate (default: 4).

Behavior:
    - Searches for all FASTA files in `input_dir`.
    - Runs Abricate sequentially for each database in `db_list`.
    - Saves output files named `<db>.abr` in `results_dir`.
    - Logs progress for each database.
    - Raises RuntimeError if no FASTA files are found.

Notes:
    - Wildcard expansion for file matching is done within the `input_dir`.
    - Temporary output files are moved to the results directory after completion.
"""

import os
import subprocess
import shutil
import glob
import logging
logger = logging.getLogger(__name__)
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def change_dir(destination: Path):
    """
    Temporarily change to the input directory with an absolute path.
    Restores the previous working directory afterward.
    """
    dest_abs = Path(destination).expanduser().resolve() 
    if not dest_abs.exists():
        raise FileNotFoundError(f"Directory does not exist: {dest_abs}")
    if not dest_abs.is_dir():
        raise NotADirectoryError(f"Not a directory: {dest_abs}")

    prev_cwd = Path.cwd().resolve()
    os.chdir(dest_abs) 
    try:
        yield
    finally:
        os.chdir(prev_cwd)

def run_abricate_bulk(input_dir, results_dir, db_list, threads=None):
    os.makedirs(results_dir, exist_ok=True)

    # Use default thread count if not provided
    if threads is None:
        threads = 4

    input_path = Path(input_dir)
    results_path = Path(results_dir)

    # Collect fasta-like files
    fasta_files = sorted(
        list(input_path.glob("*.fna")) +
        list(input_path.glob("*.fa")) +
        list(input_path.glob("*.fasta"))
    )

    if not fasta_files:
        raise RuntimeError(
            f"No input files found in {input_dir} with .fna/.fa/.fasta extensions."
        )

    with change_dir(input_path):
        for db in db_list:
            logger.info(f"Running Abricate on database: {db}")

            # Command includes all fasta files
            cmd = f"abricate {' '.join(f.name for f in fasta_files)} --db {db} -t {threads}"

            temp_output = f"{db}.abr"
            with open(temp_output, "w") as out_f:
                subprocess.run(cmd, shell=True, stdout=out_f, stderr=subprocess.DEVNULL)

            final_output_path = results_path / f"{db}.abr"
            shutil.move(temp_output, final_output_path)
            logger.info(f"Saved: {final_output_path}")
