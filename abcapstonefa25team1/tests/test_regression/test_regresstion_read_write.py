import pytest
import os
from abcapstonefa25team1.backend.utils.read_write import (
    read_file,
    write_file,
    write_encrypted_binary,
    read_encrypted_binary,
)


@pytest.mark.regression
def test_text_file_roundtrip(tmp_path):
    """Regression test: ensure read_file and write_file preserve data integrity."""
    file_path = tmp_path / "test.txt"
    text = "Regression test for read_write module!"

    # Write and read back
    write_file(file_path, text)
    read_back = read_file(file_path)


    assert read_back == text, "File content changed after write/read cycle!"
    assert file_path.exists(), "File not created!"
    assert file_path.stat().st_size > 0, "File is empty after writing!"


@pytest.mark.regression
def test_encrypted_binary_roundtrip(tmp_path):
    """Regression test: ensure write_encrypted_binary and read_encrypted_binary preserve integers."""
    file_path = tmp_path / "cipher.bin"
    n = 3233  # 61 * 53 typical RSA modulus
    cipher_blocks = [65, 123, 999, 2024]

    # Write to binary file
    write_encrypted_binary(file_path, cipher_blocks, n)
    assert os.path.exists(file_path), "Cipher file not created!"

    # Read back from binary
    read_blocks = read_encrypted_binary(file_path, n)

    
    assert read_blocks == cipher_blocks, "Binary read/write mismatch!"
    assert all(isinstance(b, int) for b in read_blocks)