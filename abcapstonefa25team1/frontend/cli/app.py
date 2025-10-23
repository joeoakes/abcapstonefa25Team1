# Project: TEAM 1 
# Purpose Details: Set up CLI to test option inputs
# Course: CMPSC488
# Author: AVIK BHUIYAN
# Date Developed: 10/18/2025
# Last Date Changed: 10/23/2025
# Revision: Setting up CLI structure for testing

import argparse
from testMethods import greet
# Define a simple function with an argument (PLACEHOLDER UNTIL CODE IS READY)

# Set up a command-line interface
def main():
    parser = argparse.ArgumentParser(description="A simple greeting tool")
    parser.add_argument("--file", "-n", required=True)

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the function with the command-line value
    greet(args.file)

if __name__ == "__main__":
    main()