import subprocess
import glob
import os
import pytest


def get_lox_files():
    """Discover all .lox test files recursively"""
    test_dir = os.path.join(os.path.dirname(__file__), "test_files")
    lox_files = glob.glob("**/*.lox", root_dir=test_dir, recursive=True)
    return sorted([os.path.join(test_dir, f) for f in lox_files])


@pytest.mark.parametrize("lox_file", get_lox_files(), ids=lambda f: os.path.basename(f))
def test_lox_file(lox_file, snapshot):
    """Test a lox file by comparing output against snapshot"""
    result = subprocess.run(
        ["python", "-m", "plox", "--print", lox_file],
        capture_output=True,
        text=True
    )
    output = result.stderr + result.stdout
    assert output == snapshot
