import pytest
from abcapstonefa25team1.backend.quantum.classical_shors import Classical_Shors


def test_even_number_factors():
    cs = Classical_Shors()
    assert cs.shors_classical(20) == (2, 10)


def test_prime_returns_none():
    cs = Classical_Shors()
    assert cs.shors_classical(13) is None


def test_perfect_power_detection():
    cs = Classical_Shors()
    # 27 = 3^3 → should return (3, 9)
    p, q = cs.shors_classical(27)
    assert p == 3 and q == 9


def test_trial_division_small_factor():
    cs = Classical_Shors()
    # 91 = 7 * 13 → trial division should catch 7
    p, q = cs.shors_classical(91)
    assert p == 7 and q == 13


def test_order_bruteforce_found():
    cs = Classical_Shors()
    # Order of 2 mod 15 is r = 4
    r = cs._order_bruteforce(2, 15, max_iterations=20)
    assert r == 4


def test_order_bruteforce_not_found():
    cs = Classical_Shors()
    # gcd(a,N) != 1 returns None
    assert cs._order_bruteforce(6, 15, max_iterations=20) is None


def test_shors_no_factor_found():
    cs = Classical_Shors()
    # 17 is prime, but caught earlier; use composite with hard factoring.
    assert cs.shors_classical(97 * 97) == (97, 97)
