"""Test FastANI and ABRicate"""

import subprocess
from unittest.mock import patch
import pytest
import tempfile
from pathlib import Path
from plasmidhub.ani import run_fastani
from plasmidhub.abricate import run_abricate_bulk


@patch("subprocess.run")
def test_run_fastani_called(mock_run):
    """Test that run_fastani calls subprocess.run and returns expected result."""
    mock_run.return_value.returncode = 0
    result = run_fastani("plasmid_list.txt")
    mock_run.assert_called()
    assert result is None or result == 0


@patch("subprocess.run")
def test_run_abricate_bulk_called_with_temp_dirs(mock_run):
    """Test run_abricate_bulk using real temporary directories and a dummy fasta file."""
    mock_run.return_value.returncode = 0

    with tempfile.TemporaryDirectory() as tmp_input_dir, tempfile.TemporaryDirectory() as tmp_results_dir:
        # Create a dummy fasta file in the temporary input directory
        dummy_fasta = Path(tmp_input_dir) / "file1.fasta"
        dummy_fasta.write_text(">seq1\nATCG")

        result = run_abricate_bulk(
            input_dir=tmp_input_dir,
            results_dir=tmp_results_dir,
            db_list=["resfinder", "ncbi"],
            threads=2,
        )

        mock_run.assert_called()
        assert result is None or result == 0

