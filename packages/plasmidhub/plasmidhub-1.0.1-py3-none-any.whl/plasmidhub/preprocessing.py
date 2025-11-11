import os
from Bio import SeqIO
import logging
logger = logging.getLogger(__name__)

VALID_NUCS = set("ACGTNacgtn-")

def validate_sequence_content(records, fname):
    """Check sequences for non-ACTGN characters and log a warning."""
    invalid_chars = set()
    for rec in records:
        invalid_chars |= set(rec.seq) - VALID_NUCS
    if invalid_chars:
        logger.warning(
            f"File {fname} contains non-standard nucleotides: {', '.join(invalid_chars)}"
        )

def validate_and_list_plasmids(input_dir):
    """
    Validate and list all plasmid FASTA files in the specified input directory.

    This function scans the provided directory for files with valid FASTA 
    extensions (.fna, .fa, .fasta), attempts to parse them, and collects 
    the absolute paths of valid plasmid files. Files that cannot be parsed 
    or contain no sequences are flagged as invalid.

    Args:
        input_dir (str): Path to the directory containing plasmid FASTA files.

    Returns:
        list: A list of absolute paths to valid plasmid FASTA files.

    Logs:
        - Warning messages listing files that are invalid or unreadable.
    """

    valid_extensions = ['.fna', '.fa', '.fasta']
    plasmid_files = []
    invalid_files = []

    for fname in os.listdir(input_dir):
        if not any(fname.lower().endswith(ext) for ext in valid_extensions):
            continue
        fpath = os.path.join(input_dir, fname)
        try:
            with open(fpath, 'r') as handle:
                records = list(SeqIO.parse(handle, 'fasta'))
                if len(records) == 0:
                    invalid_files.append(fname)
                else:
                    validate_sequence_content(records, fname)
                    plasmid_files.append(os.path.abspath(fpath))
        except Exception:
            invalid_files.append(fname)

    if invalid_files:
        logger.warning("Warning: The following files are not valid FASTA files or unreadable:")
        for f in invalid_files:
            logger.warning(f" - {f}")

    # Sort by filename - if you sort by name, it affect the layout of the plot (just the visualization, not the network itrself)!
    # plasmid_files.sort(key=lambda x: os.path.basename(x).lower())

    return plasmid_files

def write_plasmid_list(plasmid_files, output_file="Plasmid_list.txt"):
    """
    Write the list of valid plasmid file paths to a text file.

    Args:
        plasmid_files (list): List of absolute paths to plasmid FASTA files.
        output_file (str, optional): Name of the output file. Defaults to "Plasmid_list.txt".

    Returns:
        None
    """

    with open(output_file, 'w') as f:
        for path in plasmid_files:
            f.write(path + '\n')

def write_plasmid_sizes(plasmid_files, output_file="Plasmid_sizes.txt"):
    """
    Calculate and write the sizes of plasmids to a text file.

    For each plasmid FASTA file, this function sums the lengths of all 
    sequences and writes the total size (in base pairs) to an output file 
    along with the plasmid filename.

    Args:
        plasmid_files (list): List of absolute paths to plasmid FASTA files.
        output_file (str, optional): Name of the output file. Defaults to "Plasmid_sizes.txt".

    Returns:
        None

    Output File Format:
        PlasmidID   Size
        plasmid1.fna    12345
        plasmid2.fa     67890
    """

    with open(output_file, 'w') as f:
        f.write("PlasmidID\tSize\n")
        for path in plasmid_files:
            total_len = 0
            with open(path, 'r') as handle:
                for rec in SeqIO.parse(handle, 'fasta'):
                    total_len += len(rec.seq)
            f.write(f"{os.path.basename(path)}\t{total_len}\n")
