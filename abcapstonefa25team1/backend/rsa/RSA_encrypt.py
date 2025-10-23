import random

def gcd(a, b):
    while b != 0:
        a, b = b, a % b    # gcd computes the greatest common divisor of a and b. 
    return a               # it repeatedly replaces (a,b) with (b,a % b) until b becomes 0 then a is the GCD.

def modinv(a, m):
    m0, x0, x1 = m, 0, 1     # computes the modularr multiplicative inverse of a modulo m - an x such that (a*x) % m == 1
    while a > 1:            
        q = a // m
        a, m = m, a % m
        x0, x1 = x1 - q * x0, x0
    return x1 % m0

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def generate_keys():
    # Pick two distinct small primes
    primes = [p for p in range(50, 150) if is_prime(p)]
    p = random.choice(primes)
    q = random.choice([x for x in primes if x != p])

    n = p * q
    phi = (p - 1) * (q - 1)

    # Choose e such that gcd(e, phi) = 1
    e = random.choice([x for x in range(3, phi, 2) if gcd(x, phi) == 1])

    # Compute d as modular inverse of e mod phi
    d = modinv(e, phi)

    # Debug Output for screenshots / verification
    print("RSA Key Generation Debug Info:")
    print(f"p = {p}")
    print(f"q = {q}")
    print(f"n (modulus) = {n}")
    print(f"phi (Euler's Totient) = {phi}")
    print(f"e (public exponent) = {e}")
    print(f"d (private exponent) = {d}")
    print(f"Check: (e * d) % phi = {(e * d) % phi} (should be 1)")

    return ((e, n), (d, n), (p, q))

def encrypt(message, public_key):
    e, n = public_key  # unpack public key: e = exponent, n = modulus

    # determine maximum bytes per block so that integer representation < n
    max_block_size = 1  # start with 1 byte
    while 256 ** max_block_size < n:
        max_block_size += 1
    max_block_size -= 1  # step back one because loop exits after exceeding n
    if max_block_size < 1:
        raise ValueError("Modulus n too small for byte packing")

    blocks = []  # list to hold encrypted integer blocks (ciphertext)
    message_bytes = message.encode('utf-8')  # convert plaintext string to bytes (UTF-8)
    for i in range(0, len(message_bytes), max_block_size):  # iterate over bytes in chunks
        chunk = message_bytes[i:i + max_block_size]  # get current chunk of up to max_block_size bytes
        m_int = int.from_bytes(chunk, byteorder='big')  # convert chunk bytes to big-endian integer
        if m_int >= n:  # safety check to ensure integer is smaller than modulus
            raise ValueError("Message chunk integer >= modulus n")
        c_int = pow(m_int, e, n)  # perform modular exponentiation: c = m^e mod n (RSA encryption)
        blocks.append(c_int)  # append encrypted integer to ciphertext list
    return blocks  # return list of encrypted integer blocks as ciphertext

#Optional simple decrypt that matches the block packing above (keeps for test)
def decrypt(cipher_blocks, private_key):
    d, n = private_key
    message_bytes = bytearray()
    for c in cipher_blocks:
        m_int = pow(c, d, n)
        # compute how many bytes were in the original block
        # find smallest k such that m_int < 256k
        k = 1
        while m_int >= 256 ** k:
            k += 1
        chunk = m_int.to_bytes(k, byteorder='big')
        message_bytes.extend(chunk)
    return message_bytes.decode('utf-8')

# Project: TEAM 1 
# Purpose Details: Encryption Function for the RSA team assignment
# Course: IST440W
# Author: VALERIE MALICKA
# Date Developed: 10/18/2025
# Last Date Changed: 10/21/2025
# Revision: Some revisions needed to be done. Using the code that was givven to us in class to help with understanding of RSA.
