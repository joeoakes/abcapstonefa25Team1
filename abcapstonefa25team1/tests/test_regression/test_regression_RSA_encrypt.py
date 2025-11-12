import pytest
from abcapstonefa25team1.backend.rsa.RSA_encrypt import RSA


@pytest.mark.regression
def test_rsa_encryption_decryption_roundtrip():
    """Regression test: ensure RSA encryption/decryption still returns original message."""
    rsa = RSA()

    # Fixed primes for deterministic regression test
    p, q, e = 11, 13, 7
    n, d = rsa.derive_private_key_from_factors(p, q, e)

    original_message = "REGRESSION TEST RSA"
    public_key = (e, n)
    private_key = (d, n)

    # Encrypt
    cipher_blocks = rsa.encrypt(original_message, public_key)

    # Decrypt
    decrypted_message = rsa.decrypt(cipher_blocks, private_key)

    # ✅ Regression verification
    assert decrypted_message == original_message, "Decrypted message does not match original!"
    assert all(isinstance(c, int) for c in cipher_blocks)


@pytest.mark.regression
def test_invalid_character_rsa():
    """Regression test: ensure RSA still raises ValueError for characters >= modulus."""
    rsa = RSA()
    public_key = (3, 61)  # n < ord('A') = 65
    with pytest.raises(ValueError):
        rsa.encrypt("A", public_key)