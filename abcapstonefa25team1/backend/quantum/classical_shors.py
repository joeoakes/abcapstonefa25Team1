# Project:
# Purpose Details: Classical implementation of Shor's algorithm
# Course: CMPSC 488
# Author: Rob Jajko
# Date Developed: 10/22/25
# Last Date Changed: 10/22/25
# Revision: 0.1.0
import random
import math


def shor_classical(n):
    """
    Classical Shor's implementation.

    Args:
        n (int): Modulus value to factor

    Returns:
        factor1 (int): Our prime number p used to compute n
        factor2 (int): Our prime number q used to compute n
    """
    if n % 2 == 0:
        return 2

    # Try random 'a' values
    for i in range(5):  # Limit retries
        a = random.randint(2, n - 2)
        if math.gcd(a, n) != 1:
            return math.gcd(a, n)

        # Quantum step: simulate period r of a^x mod N
        r = _find_period_simulated(a, n)
        if r is None or r % 2 != 0:
            continue

        # Try to compute factors
        x = pow(a, r // 2, n)
        if x == n - 1 or x == 1:
            continue

        factor1 = math.gcd(x + 1, n)
        factor2 = math.gcd(x - 1, n)

        if factor1 * factor2 == n:
            return factor1, factor2
    return None


def _find_period_simulated(a, n):
    """
    Find the order r, here is where we'd use quantum computing.

    Args:
        a (int): Base co-prime to n
        n (int): Modulus value to factor

    Returns:
        r (int): order of a modulo n
    """
    for r in range(1, n):
        if pow(a, r, n) == 1:
            return r
    return None
