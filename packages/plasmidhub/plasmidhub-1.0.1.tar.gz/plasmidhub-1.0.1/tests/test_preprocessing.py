import os
import pytest
from plasmidhub.preprocessing import validate_and_list_plasmids

def test_validate_and_list_plasmids(tmp_path):
    # Create a valid FASTA file
    valid_fasta = tmp_path / "valid_plasmid.fasta"
    valid_fasta.write_text(">plasmid1\nACTGACTGACTG\n")

    # Create an invalid FASTA file (empty)
    invalid_fasta = tmp_path / "invalid_plasmid.fasta"
    invalid_fasta.write_text("")

    # Create a non-FASTA file (wrong extension)
    other_file = tmp_path / "notes.txt"
    other_file.write_text("This is not a fasta")

    plasmid_files = validate_and_list_plasmids(str(tmp_path))

    # Should find only the valid FASTA file
    assert len(plasmid_files) == 1
    assert os.path.basename(plasmid_files[0]) == "valid_plasmid.fasta"