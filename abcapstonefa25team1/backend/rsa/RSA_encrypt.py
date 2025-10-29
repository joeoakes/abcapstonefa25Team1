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


class RSA:
    def __init__(self):
        self.logger = logging.getLogger("sred_cli.rsa_encrypt.RSA")
        self.logger.debug("Creating an instance of logger for RSA encryption")

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

    def encrypt(self, message: str, public_key: tuple[int, int]) -> list[int]:
        e, n = public_key
        ciphertext = []
        for char in message:
            m_int = ord(char)  # get integer value of the character
            if m_int >= n:
                raise ValueError(f"Character '{char}' integer {m_int} >= modulus n={n}")
            c_int = pow(m_int, e, n)
            ciphertext.append(c_int)
        return ciphertext

    def decrypt(self, cipher_blocks: list[int], private_key: tuple[int, int]) -> str:
        d, n = private_key
        message = ""
        for c in cipher_blocks:
            m_int = pow(c, d, n)
            message += chr(m_int)
        return message

    def generate_keys(self, primes_range=(3, 50)) -> tuple:
        primes = [p for p in range(*primes_range) if self._is_prime(p)]
        p = random.choice(primes)
        q = random.choice([x for x in primes if x != p])
        n = p * q
        phi = (p - 1) * (q - 1)
        e = random.choice([x for x in range(3, phi, 2) if math.gcd(x, phi) == 1])
        d = self._modinv(e, phi)
        return ((e, n), (d, n), (p, q))

    def _modinv(self, a, m):
        m0, x0, x1 = m, 0, 1
        while a > 1:
            q = a // m
            a, m = m, a % m
            x0, x1 = x1 - q * x0, x0
        return x1 % m0

    def _is_prime(self, n):
        if n <= 1:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True
