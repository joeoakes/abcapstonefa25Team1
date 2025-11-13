import random
from abcapstonefa25team1.backend.quantum.classical_shors import Classical_Shors
import pytest
import sys
import io


from abcapstonefa25team1.backend.utils.read_write import (
    read_encrypted_binary,
    read_file,
    write_encrypted_binary,
    write_file,
)
from abcapstonefa25team1.backend.rsa.RSA_encrypt import RSA


@pytest.mark.integration
def test_full_encrypt_decrypt_cycle_classical_shors(tmp_path):
    """
    Integration test covering:
      - RSA key generation
      - File I/O for plaintext/ciphertext
      - Classical Shor’s factoring and private key derivation
      - End-to-end encryption → decryption cycle
    """

    rsa = RSA()
    random.seed(2025)

    # ----- Step 1: Generate keys -----
    pub_key, priv_key, primes = rsa.generate_keys()  # small for test speed
    e, n = pub_key
    d, _ = priv_key
    p, q = primes

    # ----- Step 2: Prepare plaintext -----
    plaintext_content = "Integration Test Message 123!"
    plaintext_file = tmp_path / "plain.txt"
    write_file(plaintext_file, plaintext_content)

    # ----- Step 3: Encrypt -----
    plaintext_read = read_file(plaintext_file)
    ciphertext = rsa.encrypt(plaintext_read, (e, n))
    assert isinstance(ciphertext, list)
    assert all(isinstance(x, int) for x in ciphertext)
    encrypted_file = tmp_path / "cipher.bin"
    write_encrypted_binary(encrypted_file, ciphertext, n)
    assert encrypted_file.exists()

    # ----- Step 4: Factor N using classical Shor -----
    shor = Classical_Shors()
    found_factors = shor.shors_classical(n)
    assert found_factors is not None, "Classical Shor's should find factors"
    fp, fq = found_factors
    assert fp * fq == n

    # ----- Step 5: Derive private key -----
    derived_priv = rsa.derive_private_key_from_factors(fp, fq, e)
    assert derived_priv is not None
    n2, d2 = derived_priv

    # ----- Step 6: Decrypt -----
    encrypted_blocks = read_encrypted_binary(encrypted_file, n2)
    decrypted_text = rsa.decrypt(encrypted_blocks, (d2, n2))

    # ----- Step 7: Verify decrypted message matches original -----
    assert decrypted_text == plaintext_content


@pytest.mark.integration
def test_cli_like_encrypt_decrypt(monkeypatch, tmp_path):
    """
    Simulates CLI behavior by capturing I/O streams.
    This test doesn’t call argparse directly, but runs through all major code paths.
    """
    rsa = RSA()

    # Redirect stdout/stderr to capture CLI prints
    stdout, stderr = io.StringIO(), io.StringIO()
    monkeypatch.setattr(sys, "stdout", stdout)
    monkeypatch.setattr(sys, "stderr", stderr)

    plaintext_file = tmp_path / "cli_input.txt"
    ciphertext_file = tmp_path / "cli_encrypted.bin"
    decrypted_file = tmp_path / "cli_decrypted.txt"

    write_file(plaintext_file, "CLI Integration Test!")

    # Generate keys for the simulated CLI encryption
    pub, priv, _ = rsa.generate_keys()
    e, n = pub
    d, _ = priv

    # Encrypt path (simulated CLI)
    plaintext = read_file(plaintext_file)
    ciphertext = rsa.encrypt(plaintext, (e, n))
    write_encrypted_binary(ciphertext_file, ciphertext, n)
    assert ciphertext_file.exists()

    # Decrypt path (simulate CLI decrypt command with classical Shor’s factoring)
    shor = Classical_Shors()
    factors = shor.shors_classical(n)
    assert factors, "Shor’s should factor the modulus"
    p, q = factors

    priv_derived = rsa.derive_private_key_from_factors(p, q, e)
    assert priv_derived, "Private key should be derivable"
    n2, d2 = priv_derived

    enc_blocks = read_encrypted_binary(ciphertext_file, n2)
    plaintext_out = rsa.decrypt(enc_blocks, (d2, n2))
    write_file(decrypted_file, plaintext_out)

    assert decrypted_file.exists()
    final_read = read_file(decrypted_file)
    assert final_read == "CLI Integration Test!"


@pytest.mark.integration
def test_handles_unfactorable_prime_rsa_key(tmp_path):
    """Ensure decrypt gracefully fails when modulus is prime (edge case)."""
    prime_modulus = 13
    e = 3
    shor = Classical_Shors()
    result = shor.shors_classical(prime_modulus)
    assert result is None, "Prime modulus should not be factorizable"
