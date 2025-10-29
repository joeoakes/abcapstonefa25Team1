# Project: TEAM 1
# Purpose Details: Encryption Function for the RSA team assignment
# Course: IST440W
# Author: VALERIE MALICKA
# Date Developed: 10/18/2025
# Last Date Changed: 10/21/2025
# Revision: Some revisions needed to be done. Using the code that was givven to us in class to help with understanding of RSA.
import random
import math
import logging
from typing import Tuple, Optional
from abcapstonefa25team1.backend.utils.read_write import (
    read_file,
    write_file,
    read_encrypted_file,
)


class RSA:
    def __init__(self):
        self.logger = logging.getLogger("sred_cli.rsa_encrypt.RSA")
        self.logger.debug("Creating an instance of logger for RSA encryption")

    def encrypt_file(
        self, input_path: str, output_path: str, public_key: tuple[int, int]
    ):
        """Encrypt plaintext file contents and write ciphertext integers to output file."""
        plaintext = read_file(input_path)
        if plaintext is None:
            return

        encrypted_blocks = self.encrypt(plaintext, public_key)
        write_file(output_path, encrypted_blocks)
        self.logger.info(f"Encrypted '{input_path}' → '{output_path}'")

    def decrypt_file(
        self, input_path: str, output_path: str, private_key: tuple[int, int]
    ):
        """Decrypt ciphertext integers from a file and write plaintext to output file."""
        encrypted_blocks = read_encrypted_file(input_path)
        if not encrypted_blocks:
            return

        decrypted_text = self.decrypt(encrypted_blocks, private_key)
        write_file(output_path, decrypted_text)
        self.logger.info(f"Decrypted '{input_path}' → '{output_path}'")

    def encrypt(self, message, public_key):
        e, n = public_key  # unpack public key: e = exponent, n = modulus

        # determine maximum bytes per block so that integer representation < n
        max_block_size = 1  # start with 1 byte
        while 256**max_block_size < n:
            max_block_size += 1
        max_block_size -= 1  # step back one because loop exits after exceeding n
        if max_block_size < 1:
            raise ValueError("Modulus n too small for byte packing")

        blocks = []  # list to hold encrypted integer blocks (ciphertext)
        message_bytes = message.encode(
            "utf-8"
        )  # convert plaintext string to bytes (UTF-8)
        for i in range(
            0, len(message_bytes), max_block_size
        ):  # iterate over bytes in chunks
            chunk = message_bytes[
                i : i + max_block_size
            ]  # get current chunk of up to max_block_size bytes
            m_int = int.from_bytes(
                chunk, byteorder="big"
            )  # convert chunk bytes to big-endian integer
            if m_int >= n:  # safety check to ensure integer is smaller than modulus
                raise ValueError("Message chunk integer >= modulus n")
            c_int = pow(
                m_int, e, n
            )  # perform modular exponentiation: c = m^e mod n (RSA encryption)
            blocks.append(c_int)  # append encrypted integer to ciphertext list
        return blocks  # return list of encrypted integer blocks as ciphertext

    # Optional simple decrypt that matches the block packing above (keeps for test)
    def decrypt(self, cipher_blocks, private_key):
        d, n = private_key
        message_bytes = bytearray()
        for c in cipher_blocks:
            m_int = pow(c, d, n)
            # compute how many bytes were in the original block
            # find smallest k such that m_int < 256k
            k = 1
            while m_int >= 256**k:
                k += 1
            chunk = m_int.to_bytes(k, byteorder="big")
            message_bytes.extend(chunk)
        return message_bytes.decode("utf-8")

    def derive_private_key_from_factors(
        self, p: int, q: int, e: int
    ) -> Optional[Tuple[int, int]]:
        """
        Given prime factors p, q and public exponent e, return (N, d)
        N = p*q, d = e^{-1} mod phi(N). Returns None if inverse doesn't exist.
        """
        N = p * q
        phi = (p - 1) * (q - 1)
        d = self._modinv(e, phi)
        if d is None:
            return None
        return (N, d)

    def generate_keys(
        self,
    ):
        # Pick two distinct small primes
        primes = [p for p in range(50, 150) if self._is_prime(p)]
        p = random.choice(primes)
        q = random.choice([x for x in primes if x != p])

        n = p * q
        phi = (p - 1) * (q - 1)

        # Choose e such that gcd(e, phi) = 1
        e = random.choice([x for x in range(3, phi, 2) if math.gcd(x, phi) == 1])

        # Compute d as modular inverse of e mod phi
        d = self._modinv(e, phi)

        # Debug Output for screenshots / verification
        self.logger.debug("RSA Key Generation Debug Info:")
        self.logger.debug(f"p = {p}")
        self.logger.debug(f"q = {q}")
        self.logger.debug(f"n (modulus) = {n}")
        self.logger.debug(f"phi (Euler's Totient) = {phi}")
        self.logger.debug(f"e (public exponent) = {e}")
        self.logger.debug(f"d (private exponent) = {d}")
        self.logger.debug(f"Check: (e * d) % phi = {(e * d) % phi} (should be 1)")

        return ((e, n), (d, n), (p, q))

    def _modinv(self, a, m):
        m0, x0, x1 = (
            m,
            0,
            1,
        )  # computes the modularr multiplicative inverse of a modulo m - an x such that (a*x) % m == 1
        while a > 1:
            q = a // m
            a, m = m, a % m
            x0, x1 = x1 - q * x0, x0
        return x1 % m0

    def _is_prime(self, n):  # test whether n is prime
        if n <= 1:
            return False  # this is a basic trial-devision primality test that checks divisibillity by every integer from 2 up
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
