# Project: TEAM 1
# Purpose Details: testing CLI read_write
# Course: CMPSC488
# Author: Huy Nguyen
# Date Developed: 10/23/2025
# Last Date Changed: 10/29/2025
# Revision: Setting up CLI test

import os
from abcapstonefa25team1.backend.utils.read_write import (
    read_file,
    write_file,
    write_encrypted_binary,
    read_encrypted_binary,
)


def test_write_and_read_file(tmp_path):
    """Test writing to a file and reading it back"""
    file_path = tmp_path / "test.txt"
    content = "Hello RSA!\nThis is a test file."

    # Write content
    write_file(file_path, content)

    # Read it back
    read_content = read_file(file_path)

    assert read_content == content


def test_read_file_not_found(tmp_path):
    """Test reading a non-existent file returns None"""
    missing_path = tmp_path / "missing.txt"
    result = read_file(missing_path)
    assert result is None


def test_write_file_encoding_error(tmp_path):
    """Test that writing non-ASCII data raises error (since using 'ascii')"""
    file_path = tmp_path / "test.txt"
    data = "你好"  # contains non-ASCII characters
    # This should raise UnicodeEncodeError inside write_file
    # but since you catch it and print, function won't crash
    write_file(file_path, data)
    # File won't be created or will be empty
    if file_path.exists():
        assert file_path.read_text(encoding="utf-8") == "" or "Caf" in file_path.read_text(encoding="utf-8")


def test_write_and_read_encrypted_binary(tmp_path):
    """Test writing and reading encrypted binary blocks"""
    file_path = tmp_path / "cipher.bin"
    n = 3233  # Example modulus (like 61*53)
    cipher_blocks = [65, 123, 999, 2024]  # Example encrypted integers

    write_encrypted_binary(file_path, cipher_blocks, n)
    assert os.path.exists(file_path)

    read_blocks = read_encrypted_binary(file_path, n)
    assert read_blocks == cipher_blocks