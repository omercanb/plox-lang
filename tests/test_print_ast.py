import glob
import os
import subprocess

import pytest


def get_all_lox_files():
    """Get all .lox test files"""
    test_dir = os.path.join(os.path.dirname(__file__), "test_files")
    lox_files = glob.glob("**/*.lox", root_dir=test_dir, recursive=True)
    return sorted([os.path.join(test_dir, f) for f in lox_files])


@pytest.mark.parametrize(
    "lox_file", get_all_lox_files(), ids=lambda f: os.path.basename(f)
)
def test_print_ast(lox_file):
    """Test that --print flag works for all language features without crashing"""

    result = subprocess.run(
        ["python", "-m", "plox", "--print", lox_file],
        capture_output=True,
        text=True,
    )
    # Should not crash - verify exit code is 0
    assert result.returncode == 0, f"AST printer crashed on {lox_file}: {result.stderr}"
    # Should produce some output
    assert len(result.stdout) > 0, f"No AST output produced for {lox_file}"
