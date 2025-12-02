# Project: TEAM 1
# Purpose Details: Encryption Function for the RSA team assignment
# Course: IST440W
# Author: VALERIE MALICKA
# Date Developed: 10/18/2025
# Last Date Changed: 10/21/2025
# Revision: Some revisions needed to be done. Using the code that was givven to us in class to help with understanding of RSA.


import random
import math
from typing import Optional, Tuple, List

class RSA:
    """Minimal RSA implementation matching the professor example."""

    def is_prime(self, n: int) -> bool:
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0:
            return False
        r = int(n**0.5)
        for i in range(3, r + 1, 2):
            if n % i == 0:
                return False
        return True

    def _egcd(self, a: int, b: int) -> Tuple[int, int, int]:
        if b == 0:
            return (a, 1, 0)
        g, x1, y1 = self._egcd(b, a % b)
        return (g, y1, x1 - (a // b) * y1)

    def modinv(self, a: int, m: int) -> Optional[int]:
        a = a % m
        g, x, _ = self._egcd(a, m)
        if g != 1:
            return None
        return x % m

    def derive_private_key_from_factors(self, p: int, q: int, e: int) -> Optional[Tuple[int,int]]:
        """Return private key (d, n) given primes p,q and public exponent e."""
        if not (self.is_prime(p) and self.is_prime(q)):
            raise ValueError("p and q must be prime")
        n = p * q
        phi = (p - 1) * (q - 1)
        d = self.modinv(e, phi)
        if d is None:
            return None
        return (d, n)

    def generate_keys(self, use_example: bool = False) -> Tuple[Tuple[int,int], Tuple[int,int], Tuple[int,int]]:
        """
        Return ((e,n), (d,n), (p,q)).
        By default generates small random primes; if use_example=True returns the professor example.
        """
        if use_example:
            p, q = 61, 53
            n = p * q
            e = 17
            d = self.modinv(e, (p-1)*(q-1))
            return ((e, n), (d, n), (p, q))

        primes = [x for x in range(50, 150) if self.is_prime(x)]
        if len(primes) < 2:
            raise RuntimeError("Not enough primes in range")
        p = random.choice(primes)
        q = random.choice([x for x in primes if x != p])
        n = p * q
        phi = (p - 1) * (q - 1)
        e_candidates = [x for x in range(3, phi, 2) if math.gcd(x, phi) == 1]
        if not e_candidates:
            return self.generate_keys(use_example=False)
        e = random.choice(e_candidates)
        d = self.modinv(e, phi)
        return ((e, n), (d, n), (p, q))

    def encrypt(self, message: str, public_key: Tuple[int,int]) -> List[int]:
        """Encrypt a string message using public_key (e, n). Returns list of integers."""
        e, n = public_key
        if not (1 < e < n):
            raise ValueError("Invalid public key")
        ciphertext = []
        for ch in message:
            m = ord(ch)
            if m >= n:
                raise ValueError(f"Plaintext integer {m} >= modulus n={n}")
            ciphertext.append(pow(m, e, n))
        return ciphertext

    def decrypt(self, ciphertext: List[int], private_key: Tuple[int,int]) -> str:
        """Decrypt list of integers using private_key (d, n). Returns string."""
        d, n = private_key
        if not (1 < d < n):
            raise ValueError("Invalid private key")
        chars = [chr(pow(c, d, n)) for c in ciphertext]
        return ''.join(chars)
