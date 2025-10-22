import os

def test_export_scripts_exist():
    assert os.path.exists("export_matches.ps1")
    assert os.path.exists("merge_latest.ps1")
