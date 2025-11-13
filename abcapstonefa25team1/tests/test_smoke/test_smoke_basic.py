import pytest

from abcapstonefa25team1.backend.rsa.RSA_encrypt import RSA
from abcapstonefa25team1.backend.quantum.quantum_shors import Quantum_Shors

# Import your file I/O functions if available
try:
    from abcapstonefa25team1.backend.utils.read_write import (
        read_file,
        write_file,
        write_encrypted_binary,
        read_encrypted_binary,
    )
except ImportError:
    read_file = write_file = write_encrypted_binary = read_encrypted_binary = None


def test_imports_succeed():
    """Smoke test: Ensure all critical modules import successfully."""
    assert RSA is not None
    assert Quantum_Shors is not None


def test_rsa_basic_cycle():
    """Smoke test: Simple RSA encryption + decryption."""
    rsa = RSA()
    public_key, private_key, primes = rsa.generate_keys()
    plaintext = "OK"

    # Encrypt and decrypt
    ciphertext = rsa.encrypt(plaintext, public_key)
    assert isinstance(ciphertext, list), "Ciphertext should be list of ints"
    decrypted = rsa.decrypt(ciphertext, private_key)

    # Just make sure it round-trips correctly
    assert decrypted == plaintext, "RSA encryption-decryption failed"
