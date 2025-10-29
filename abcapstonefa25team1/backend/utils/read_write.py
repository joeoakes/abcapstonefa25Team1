# -----------------------------------------------------------
# Project:
# Purpose Details: Handles reading and writing text files
# Course: CMPSC 488
# Author: Kamila Anarkulova
# Date Developed: October 21, 2025
# Last Date Changed: October 21, 2025
# Revision: 1.0 - Initial version, created file read/write functions
# -----------------------------------------------------------


def read_file(file_path):
    # Read and return text content from file
    try:
        # Open file in read mode with UTF-8 encoding to handle all characters
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()  # Read the entire content of the file
        return data

    except FileNotFoundError:
        # File not found – print an error message
        print(f"Error: file {file_path} not found")
        return None

    except Exception as e:
        # Handle any other unexpected error
        print(f"Error reading file: {e}")
        return None


def write_file(file_path, data):
    # Write(save) text content to a file.
    try:
        # Open file in write mode with UTF-8 encoding
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(
                " ".join(str(n) for n in data)
            )  # Write the provided data to the file
        print(f"File saved successfully as '{file_path}'")

    except Exception as e:
        # Handle unexpected write errors
        print(f"Error writing file:{e}")


def read_encrypted_file(file_path):
    """Read a file of space-separated encrypted integers and return as list[int]."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [int(x) for x in f.read().split()]
    except Exception as e:
        print(f"Error reading encrypted file: {e}")
        return []


def write_encrypted_binary(file_path, cipher_blocks, n):
    """Write encrypted integers to file as binary (fixed block size)."""
    block_size = (n.bit_length() + 7) // 8
    with open(file_path, "wb") as f:
        for c in cipher_blocks:
            f.write(c.to_bytes(block_size, "big"))


def read_encrypted_binary(file_path, n):
    """Read encrypted integers from binary file."""
    block_size = (n.bit_length() + 7) // 8
    cipher_blocks = []
    with open(file_path, "rb") as f:
        while chunk := f.read(block_size):
            cipher_blocks.append(int.from_bytes(chunk, "big"))
    return cipher_blocks
