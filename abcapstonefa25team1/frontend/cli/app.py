# Project: TEAM 1
# Purpose Details: Set up CLI to test option inputs
# Course: CMPSC488
# Author: AVIK BHUIYAN
# Date Developed: 10/18/2025
# Last Date Changed: 10/23/2025
# Revision: Setting up CLI structure and added same method

import logging
import argparse
import sys
import os


# Try package imports first; if running file directly, add project root to sys.path and retry.
try:
    from abcapstonefa25team1.backend.utils.read_write import read_file
    from abcapstonefa25team1.backend.quantum import classical_shors
except Exception:
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from abcapstonefa25team1.backend.utils.read_write import read_file
    from abcapstonefa25team1.backend.quantum import classical_shors

# Define a simple function with an argument (PLACEHOLDER UNTIL CODE IS READY)


# Set up a command-line interface
def main():
    parser = argparse.ArgumentParser(description="sred a quantum cryptography tool")
    parser.add_argument("INPUT")
    parser.add_argument("--output", "-o", required=False)
    parser.add_argument(
        "--modulus", "-m", nargs="?", type=int, default=15, const=15, required=False
    )
    parser.add_argument("--encrypt", "-e", action="store_true")
    parser.add_argument("--classical", "-c", action="store_false")
    parser.add_argument(
        "-d",
        "--debug",
        help="Print lots of debugging statements",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Be verbose",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
        default=logging.WARNING,
    )  # Parse the command-line arguments

    args = parser.parse_args()
    logger = logging.getLogger("sred_cli")
    logger.setLevel(args.loglevel)

    # create file handler which logs even debug messages
    fh = logging.FileHandler("cli_output.log")
    fh.setLevel(args.loglevel)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(args.loglevel)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    fileText = read_file(args.INPUT)
    logger.info(f"Read File: {fileText}")

    shors = classical_shors.Classical_Shors()

    if not args.encrypt:
        p, q = shors.shors_classical(int(args.modulus))
        logger.info(f"Shor's Algorithm Output: {p} {q}")
    else:
        logger.debug("Encryption:")


if __name__ == "__main__":
    main()
