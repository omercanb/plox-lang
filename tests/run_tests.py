import glob
import os
import subprocess
import sys
from pprint import pprint


def unexpected(previous_output, current_output, lox_file):
    print(f"test failed on file '{os.path.split(lox_file)[1]}'")
    print("file start")
    print(open(lox_file).read())
    print("file end")
    print(previous_output)
    if not previous_output or previous_output.isspace():
        print("no previous output")
        print(f"current output start")
        print(current_output)
        print(f"current output end")
    else:
        print(f"output not matched for '{os.path.split(lox_file)[1]}'")
        print(f"previous output start")
        print(previous_output)
        print(f"previous output end")
        print(f"current output start")
        print(current_output)
        print(f"current output end")

    choice = input("is this correct? [y, n]: ")
    if choice == 'n':
        sys.exit(1)
    if choice != 'y': 
        print('please enter y or n')
        sys.exit(1)
    # Choice is y
    with open(lox_file + ".expected", "w") as f:
        f.write(current_output)

test_dir = "test_files"

lox_files = glob.glob("*.lox", root_dir=test_dir)
lox_files = map(lambda x: os.path.join(test_dir, x), lox_files)

for lox_file in lox_files:
    print(f"Running '{os.path.split(lox_file)[1]}'")
    result = subprocess.run(['plox', '--print', lox_file], capture_output=True)
    current_output = result.stderr.decode() + result.stdout.decode()

    expected_file = lox_file + '.expected'
    if not os.path.isfile(expected_file):
        previous_output = ""
    else:
        with open(expected_file, "r") as f:
            previous_output = f.read()
    if current_output == previous_output:
        print(f"Test Passed For '{lox_file}'")
    else:
        unexpected(previous_output, current_output, lox_file)

# Grab all lox files
# Run the lox files capturing all that you need to
# Check that the expected file contains the same
# If it doesn't or the test file doesn't exist ask the user if it's correct

