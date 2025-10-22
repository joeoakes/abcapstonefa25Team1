import pytest
from abcapstonefa25team1.backend.rsa import RSA_encrypt


def test_gcd():
    assert RSA_encrypt.gcd(48, 18) == 6
    assert RSA_encrypt.gcd(7, 3) == 1


def test_modinv():
    a, m = 3, 26
    inv = RSA_encrypt.modinv(a, m)
    # check modular inverse correctness
    assert (a * inv) % m == 1


def test_is_prime():
    assert RSA_encrypt.is_prime(7) is True
    assert RSA_encrypt.is_prime(10) is False
    assert RSA_encrypt.is_prime(1) is False


def test_generate_keys_valid():
    public_key, private_key, primes = RSA_encrypt.generate_keys()
    e, n = public_key
    d, _ = private_key
    p, q = primes

    # n must equal p*q
    assert n == p * q
    # gcd(e, phi) should equal 1
    phi = (p - 1) * (q - 1)
    assert RSA_encrypt.gcd(e, phi) == 1
    # d should be modular inverse of e mod phi
    assert (e * d) % phi == 1


def test_encrypt_decrypt_roundtrip():
    public_key, private_key, _ = RSA_encrypt.generate_keys()
    message = "Hello RSA"
    ciphertext = RSA_encrypt.encrypt(message, public_key)
    plaintext = RSA_encrypt.decrypt(ciphertext, private_key)
    assert plaintext == message

