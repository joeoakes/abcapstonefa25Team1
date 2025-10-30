# Project: TEAM 1
# Purpose Details: unit test for RSA
# Course: CMPSC488
# Author: Huy Nguyen
# Date Developed: 10/23/2025
# Last Date Changed: 10/29/2025
# Revision: fixed the unit test
import pytest
from abcapstonefa25team1.backend.rsa.RSA_encrypt import RSA


@pytest.fixture
def rsa():
    """define fixture name rsa to avoid repeatation
    instread of: 
    def test_encrypt():
    rsa = RSA()
    we can do 
    def test_encrypt(rsa):"""
    return RSA()


def test_is_prime(rsa):
    """checking if is_prime is working properly"""
    assert rsa._is_prime(7) is True
    assert rsa._is_prime(1) is False
    assert rsa._is_prime(9) is False


def test_modinv(rsa):
    """checking if mod is working properly"""
    assert rsa._modinv(3, 40) == 27  # since (3*27) % 40 == 1


def test_derive_private_key(rsa):
    """testing if d is modular inverse of e mod phi before encrypt"""
    p, q, e = 11, 13, 7
    result = rsa.derive_private_key_from_factors(p, q, e)
    assert result is not None
    n, d = result
    phi = (p - 1) * (q - 1)
    assert (e * d) % phi == 1  # d must be modular inverse of e mod phi


def test_generate_keys(rsa):
    """Test that generate_keys produces valid RSA keys"""
    public_key, private_key, (p, q) = rsa.generate_keys((11, 30))
    e, n = public_key
    d, _ = private_key
    phi = (p - 1) * (q - 1)

    # e and phi should be coprime
    assert (e > 1) and (e < phi)
    assert (d * e) % phi == 1
    assert n == p * q


def test_encrypt(rsa):
    """Test encrypt returns integer list and raises error for invalid chars"""
    public_key, _, _ = rsa.generate_keys((11, 30))
    message = "HI"
    cipher = rsa.encrypt(message, public_key)

    assert isinstance(cipher, list)
    assert all(isinstance(c, int) for c in cipher)

    # Force a too-small modulus to trigger ValueError
    small_key = (3, 61)  # n=61 < ord("A")=65
    with pytest.raises(ValueError):
        rsa.encrypt("A", small_key)


def test_decrypt(rsa):
    """Test decrypt correctly reverses encryption"""
    public_key, private_key, _ = rsa.generate_keys((11, 30))
    message = "HELLO"
    cipher = rsa.encrypt(message, public_key)
    decrypted = rsa.decrypt(cipher, private_key)

    assert decrypted == message

