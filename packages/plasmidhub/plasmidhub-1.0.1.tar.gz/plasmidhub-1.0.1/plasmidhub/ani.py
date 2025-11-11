"""
Run FastANI to calculate pairwise Average Nucleotide Identity (ANI) between plasmid sequences.

This script runs the FastANI tool using the same plasmid list as both query and reference to compute
pairwise similarity. The results are written to `fastani_raw_results.tsv` in the specified output directory.

Parameters:
    plasmid_list_file (str): Path to a text file containing a list of plasmid FASTA files.
    fragLen (int, optional): Fragment length used, user defined (default: 1000).
    minFrag (int, optional): Minimum number of matching fragments required, user defined (default: 3).
    kmer (int, optional): K-mer size, user defined (default: 14).
    output_dir (str, optional): Directory to save the FastANI results.
    threads (int, optional): Number of threads to use (default: 4).
"""

import os
import subprocess
import logging
logger = logging.getLogger(__name__)

def run_fastani(plasmid_list_file, fragLen=1000, minFrag=3, kmer=14, output_dir=".", threads=None):
    if threads is None:
        threads = 4

    output_file = os.path.join(output_dir, "fastani_raw_results.tsv")
    cmd = [
        "fastANI",
        "--ql", plasmid_list_file,
        "--rl", plasmid_list_file,
        "-o", output_file,
        "--fragLen", str(fragLen),
        "--minFraction", str(minFrag),
        "--kmer", str(kmer),
        "-t", str(threads)
    ]
    logger.info("Running FastANI with command:")
    logger.info(" ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("FastANI failed with error:")
        logger.error(result.stderr)
        exit(1)
    else:
        logger.info("FastANI completed successfully.")
