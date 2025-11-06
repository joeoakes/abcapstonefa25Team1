# Project: TEAM 1
# Purpose Details: Encryption Function for the RSA team assignment
# Course: IST440W
# Author: VALERIE MALICKA
# Date Developed: 10/18/2025
# Last Date Changed: 10/21/2025
# Revision: Some revisions needed to be done. Using the code that was givven to us in class to help with understanding of RSA.

import random  # for generating random primes and keys
import math    # for gcd calculation
import logging  # for logging debug information
from typing import Tuple, Optional  # type hints for clarity


class RSA:
    def __init__(self):
        # Set up a logger for debugging RSA operations
        self.logger = logging.getLogger("sred_cli.rsa_encrypt.RSA")
        self.logger.debug("Creating an instance of logger for RSA encryption")

    def derive_private_key_from_factors(
        self, p: int, q: int, e: int
    ) -> Optional[Tuple[int, int]]:
        """
        Derives the private key from prime factors p, q and public exponent e.
        Returns a tuple (N, d) where:
            N = p * q
            d = modular inverse of e modulo phi(N)
        Returns None if modular inverse does not exist.
        """
        N = p * q  # modulus
        phi = (p - 1) * (q - 1)  # Euler's totient function
        d = self._modinv(e, phi)  # compute modular inverse
        if d is None:
            return None
        return (N, d)  # return modulus and private exponent

    def encrypt(self, message: str, public_key: tuple[int, int]) -> list[int]:
        """
        Encrypts a message string using the provided public key (e, n).
        Returns a list of integers representing the ciphertext.
        """
        e, n = public_key
        ciphertext = []
        for char in message:
            m_int = ord(char)  # convert character to integer
            if m_int >= n:
                # Cannot encrypt if integer representation >= modulus
                raise ValueError(f"Character '{char}' integer {m_int} >= modulus n={n}")
            c_int = pow(m_int, e, n)  # RSA encryption: c = m^e mod n
            ciphertext.append(c_int)
        return ciphertext

    def decrypt(self, cipher_blocks: list[int], private_key: tuple[int, int]) -> str:
        """
        Decrypts a list of integers (cipher_blocks) using private key (d, n).
        Returns the decrypted message as a string.
        """
        d, n = private_key
        message = ""
        for c in cipher_blocks:
            m_int = pow(c, d, n)  # RSA decryption: m = c^d mod n
            message += chr(m_int)  # convert integer back to character
        return message

    def generate_keys(self, primes_range=(3, 50)) -> tuple:
        """
        Generates RSA keys:
            - Public key (e, n)
            - Private key (d, n)
            - Prime factors (p, q)
        Primes are selected randomly within primes_range.
        """
        # List all prime numbers in the given range
        primes = [p for p in range(*primes_range) if self._is_prime(p)]
        p = random.choice(primes)  # pick first prime
        q = random.choice([x for x in primes if x != p])  # pick second prime, not equal to p
        n = p * q
        phi = (p - 1) * (q - 1)
        # Pick public exponent e coprime to phi
        e = random.choice([x for x in range(3, phi, 2) if math.gcd(x, phi) == 1])
        d = self._modinv(e, phi)  # compute private exponent
        return ((e, n), (d, n), (p, q))  # return public key, private key, primes

    def _modinv(self, a, m):
        """
        Computes modular inverse of a modulo m using Extended Euclidean Algorithm.
        Returns x such that (a*x) % m == 1
        """
        m0, x0, x1 = m, 0, 1
        while a > 1:
            q = a // m
            a, m = m, a % m
            x0, x1 = x1 - q * x0, x0
        return x1 % m0

    def _is_prime(self, n):
        """
        Checks if a number n is prime.
        Returns True if n is prime, False otherwise.
        """
        if n <= 1:
            return False
        # Check divisibility up to sqrt(n)
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
                return False
        return True
