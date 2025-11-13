# Project: TEAM 1
# Purpose Details: Set up CLI to test option inputs
# Course: CMPSC488
# Author: AVIK BHUIYAN
# Date Developed: 10/18/2025
# Last Date Changed: 10/23/2025
# Revision: Setting up CLI structure and added same method


import logging
import argparse
from abcapstonefa25team1.backend.rsa import RSA_encrypt
from abcapstonefa25team1.backend.utils.read_write import (
    read_encrypted_binary,
    read_file,
    write_encrypted_binary,
    write_file,
)
from abcapstonefa25team1.backend.quantum import classical_shors, quantum_shors


def main():
    parser = argparse.ArgumentParser(description="sred a quantum cryptography tool")
    sub_parser = parser.add_subparsers(dest="command", required=True)

    # Global debug/verbose
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
    )

    # Encrypt subcommand
    encrypt_parser = sub_parser.add_parser("encrypt", help="Encrypt a file")
    encrypt_parser.add_argument("INPUT", type=str, help="File to encrypt")
    encrypt_parser.add_argument(
        "--output", "-o", required=False, type=str, help="Output file name"
    )
    encrypt_parser.add_argument(
        "--keys",
        "-k",
        nargs=2,
        type=int,
        default=[7, 123],
        help="Public key: e n (must be greater than 122)",
    )

    # Decrypt subcommand
    decrypt_parser = sub_parser.add_parser("decrypt", help="Decrypt a file")
    decrypt_parser.add_argument("INPUT", type=str, help="File to decrypt")
    decrypt_parser.add_argument(
        "--output", "-o", required=False, type=str, help="Output file name"
    )
    decrypt_parser.add_argument(
        "--classical", "-c", action="store_true", help="Use classical Shor’s algorithm"
    )
    decrypt_parser.add_argument(
        "--exponent",
        "-e",
        type=int,
        default=7,
        help="Public exponent e",
    )
    decrypt_parser.add_argument(
        "--modulus",
        "-m",
        type=int,
        default=123,
        help="Public modulus n, must be greater than 122",
    )

    args = parser.parse_args()
    logger = logging.getLogger("sred_cli")
    logger.setLevel(args.loglevel)

    ch = logging.StreamHandler()
    ch.setLevel(args.loglevel)
    ch.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(ch)

    rsa = RSA_encrypt.RSA()

    # ---- Encrypt ----
    if args.command == "encrypt":
        if args.keys:
            e, n = args.keys
            if n < 123:
                print("Error: Modulus must be greater than 122")
                return
            logger.info(f"Encrypting using public key (e={e}, n={n})")
        else:
            public_key, private_key, _ = rsa.generate_keys()
            e, n = public_key
            logger.info(f"Generated public key: {public_key}")
            logger.info(f"Generated private key: {private_key}")

        plaintext = read_file(args.INPUT)
        if plaintext is None:
            print("Error: Failed to read input file.")
            return

        ciphertext = rsa.encrypt(plaintext, (e, n))
        if args.output:
            write_encrypted_binary(args.output, ciphertext, n)
            print(f"Encrypted output saved to {args.output}")
        else:
            print(ciphertext)

    # ---- Decrypt ----
    elif args.command == "decrypt":
        N = args.modulus
        if N < 123:
            print("Error: Modulus must be greater than 122")
            return

        e = args.exponent

        # Factor N using chosen Shor’s implementation
        if args.classical:
            shors = classical_shors.Classical_Shors()
            factors = shors.shors_classical(N)
            if not factors:
                print("Classical Shor’s failed to factor N.")
                return
            p, q = factors
            logger.info(f"Classical Shor’s found p={p}, q={q}")
        else:
            shors = quantum_shors.Quantum_Shors()
            factors = shors.run_shors_algorithm(N, 15)
            if not factors:
                print("Quantum Shor's failed to factor N.")
                return
            p, q = factors
            logger.info(f"Quantum Shor’s found p={p}, q={q}")

        # Derive private key from Shor's factors
        priv = rsa.derive_private_key_from_factors(p, q, e)
        if priv is None:
            logger.error("Error: Failed to derive private key.")
            return
        d, n = priv[1], priv[0]

        encrypted_blocks = read_encrypted_binary(args.INPUT, n)
        if encrypted_blocks is None:
            print("Error: Failed to read input file.")
            return

        plaintext = rsa.decrypt(encrypted_blocks, (d, n))
        if args.output:
            write_file(args.output, plaintext)
            print(f"Decrypted output saved to {args.output}")
        else:
            print(plaintext)


if __name__ == "__main__":
    main()
