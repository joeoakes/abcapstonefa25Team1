# Project: PSU Abington Fall 2025 Capstone
# Purpose Details: Classical implementation of Shor's algorithm
# Course: CMPSC 488
# Author: Rob Jajko
# Date Developed: 10/22/25
# Last Date Changed: 10/22/25
# Revision: 0.1.0
import logging
import random
import math
from typing import Optional, Tuple


class Classical_Shors:
    def __init__(self):
        self.logger = logging.getLogger("sred_cli.classical_shors.Classical_Shors")
        self.logger.debug("Creating an instance of logger for Shor's Classical")

    def shors_classical(self, N: int, tries: int = 10) -> Optional[Tuple[int, int]]:
        """
        Attempt to factor N using the classical analog of Shor's algorithm.
        Tries up to `tries` random choices of a.
        Returns a tuple (p, q) of non-trivial factors if found, otherwise None.
        
        Args:
            N: The integer to be factored (must be greater than 1).
            tries: Maximum number of random attempts to find factors. Defaults to 10.

        Returns:
            A tuple containing two non-trivial factors (p, q)
            of N if successful; otherwise, None.
        """
        if N % 2 == 0:
            return (2, N // 2)
        if N <= 3:
            return None
        # perfect power check
        pp = self._is_power(N)
        if pp is not None:
            base, k = pp
            self.logger.debug(f"N = {N} is a perfect power: {base}^{k}")
            return (base, N // base)

        # quick small-factor trial division
        small = self._trial_division(N, limit=1000)
        if small:
            return (small, N // small)

        for attempt in range(1, tries + 1):
            a = random.randrange(2, N - 1)
            g = math.gcd(a, N)
            if g > 1:
                # we lucked into a nontrivial factor
                self.logger.debug(
                    f"Attempt {attempt}: gcd({a}, {N}) = {g} -> found factor"
                )
                return (g, N // g)

            # find order r of a mod N (classical brute-force replacement for quantum subroutine)
            r = self._order_bruteforce(a, N, max_iterations=N)
            if r is None:
                self.logger.debug(
                    f"Attempt {attempt}: no order found within bound for a={a}"
                )
                continue
            self.logger.debug(f"Attempt {attempt}: chosen a={a}, order r={r}")

            # r must be even and a^(r/2) not congruent to -1 mod N
            if r % 2 != 0:
                self.logger.debug("r is odd, try again")
                continue

            ar2 = pow(a, r // 2, N)
            if ar2 == N - 1:
                self.logger.debug("a^(r/2) ≡ -1 (mod N), try again")
                continue

            # compute potential factors
            p = math.gcd(ar2 + 1, N)
            q = math.gcd(ar2 - 1, N)
            if 1 < p < N:
                self.logger.debug(f"Found factors: {p} and {N // p}")
                return (p, N // p)
            if 1 < q < N:
                self.logger.debug(f"Found factors: {q} and {N // q}")
                return (q, N // q)
            # otherwise try again
            self.logger.debug("GCDs gave trivial factors, try again")

        # failed after tries
        self.logger.debug("Failed to find factor with given tries")
        return None

    def _is_power(self, n: int) -> Optional[Tuple[int, int]]:
        """
        Return (b, k) if n == b**k for k>=2, else None. Quick detection of perfect powers.
        
        Args: 
            N: The integer to check.

        Returns:
            A tuple (b, k) if n is a perfect power, otherwise None.
        """
        if n <= 1:
            return None
        max_k = int(math.log2(n)) + 1
        for k in range(2, max_k + 1):
            b = round(n ** (1.0 / k))
            if b > 1 and b**k == n:
                self.logger.debug(f"Is Power: {b}, {k}")
                return (b, k)
        return None

    def _trial_division(self, n: int, limit: int = 1000) -> Optional[int]:
        """
        Try small prime factors up to `limit`. Return factor or None.
        
        Args: 
            N: The integer to factor.
            limit: The upper bound for trial division.
        Returns:
            A non-trivial factor of n if found, otherwise None.
        
        """
        if n % 2 == 0:
            return 2
        p = 3
        while p <= limit and p * p <= n:
            if n % p == 0:
                self.logger.debug(f"Trial Division: {p}")
                return p
            p += 2
        return None

    def _order_bruteforce(
        self, a: int, N: int, max_iterations: int = 0
    ) -> Optional[int]:
        """
        Find the multiplicative order r of a modulo N by brute force:
        the smallest r > 0 such that a^r % N == 1.
        Returns r or None if not found within max_iterations.

        Args: 
            a: The base integer.
            N: The modulus.
            max_iterations: Maximum number of iterations to attempt.
        Returns:
            The multiplicative order r if found within iteration limit, otherwise None.
        """
        if math.gcd(a, N) != 1:
            return None
        if max_iterations is None:
            # A safe (but large) upper bound: phi(N) <= N-1, but we set it to N for simplicity
            max_iterations = N
        cur = 1
        for r in range(1, max_iterations + 1):
            cur = (cur * a) % N
            if cur == 1:
                return r
        return None
