# Project: TEAM 1 
# Purpose Details: Set up CLI to test option inputs
# Course: CMPSC488
# Author: AVIK BHUIYAN
# Date Developed: 10/18/2025
# Last Date Changed: 10/23/2025
# Revision: Setting up CLI structure and added same method

import argparse
import ast
import sys
import os

# Try package imports first; if running file directly, add project root to sys.path and retry.
try:
    from abcapstonefa25team1.backend.quantum.classical_shors import shor_classical
    from abcapstonefa25team1.backend.utils.read_write import read_file
except Exception:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from abcapstonefa25team1.backend.quantum.classical_shors import shor_classical
    from abcapstonefa25team1.backend.utils.read_write import read_file

# Define a simple function with an argument (PLACEHOLDER UNTIL CODE IS READY)

# Set up a command-line interface
def main():
    parser = argparse.ArgumentParser(description="A simple greeting tool")
    parser.add_argument("--file", "-n", required=True)

    # Parse the command-line arguments
    args = parser.parse_args()
    fileText = read_file(args.file)
    print(fileText)

    shorsOutput = shor_classical(int(fileText))
    print(f"Shor's Algorithm Output: {shorsOutput}")

if __name__ == "__main__":
    main()