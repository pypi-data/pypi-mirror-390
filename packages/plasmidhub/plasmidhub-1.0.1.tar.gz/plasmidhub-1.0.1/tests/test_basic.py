import importlib
import subprocess

def test_import_modules():
    # Test import of core modules
    import plasmidhub.preprocessing
    import plasmidhub.ani
    import plasmidhub.clustering

def test_cli_version():
    result = subprocess.run(["plasmidhub", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "plasmidhub" in result.stdout.lower()
    assert "1.0.1" in result.stdout
