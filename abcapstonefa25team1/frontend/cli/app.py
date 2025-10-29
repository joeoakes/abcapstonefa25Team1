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
from abcapstonefa25team1.backend.utils.read_write import read_file, write_file
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
        "--keys", "-k", nargs=2, type=int, help="Public key: e n"
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
        "--exponent", "-e", type=int, required=True, help="Public exponent e"
    )
    decrypt_parser.add_argument(
        "--modulus", "-m", type=int, required=True, help="Public modulus n"
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

    # Encrypt
    if args.command == "encrypt":
        plaintext = read_file(args.INPUT)
        if plaintext is None:
            logger.error("Failed to read input file.")
            return

        if args.keys:
            e, n = args.keys
            logger.info(f"Encrypting using public key (e={e}, n={n})")
            ciphertext = rsa.encrypt(plaintext, (e, n))
        else:
            public_key, private_key, _ = rsa.generate_keys()
            e, n = public_key
            logger.info(f"Generated public key: {public_key}")
            logger.info(f"Generated private key: {private_key}")
            ciphertext = rsa.encrypt(plaintext, public_key)

        output_file = args.output or "encrypted.txt"
        write_file(output_file, ciphertext)
        logger.info(f"Encrypted output saved to '{output_file}'")

    # Decrypt
    elif args.command == "decrypt":
        # Read encrypted integers (space-separated)
        file_text = read_file(args.INPUT)
        if file_text is None:
            logger.error("Failed to read input file.")
            return

        try:
            encrypted_blocks = [int(x) for x in file_text.split()]
        except ValueError:
            logger.error("Ciphertext file must contain space-separated integers.")
            return

        N = args.modulus
        e = args.exponent

        # Factor N using chosen Shor’s implementation
        if args.classical:
            shors = classical_shors.Classical_Shors()
            factors = shors.shors_classical(N)
            if not factors:
                logger.error("Classical Shor’s failed to factor N.")
                return
            p, q = factors
            logger.info(f"Classical Shor’s found p={p}, q={q}")
        else:
            shors = quantum_shors.Quantum_Shors()
            p, q = shors.shors_quantum(N)
            logger.info(f"Quantum Shor’s found p={p}, q={q}")

        priv = rsa.derive_private_key_from_factors(p, q, e)
        if priv is None:
            logger.error("Failed to derive private key.")
            return

        d, n = priv[1], priv[0]
        plaintext = rsa.decrypt(encrypted_blocks, (d, n))

        output_file = args.output or "decrypted.txt"
        write_file(output_file, plaintext)
        logger.info(f"Decrypted output saved to '{output_file}'")


if __name__ == "__main__":
    main()
