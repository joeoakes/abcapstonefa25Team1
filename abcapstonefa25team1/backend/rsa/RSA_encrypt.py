# Project: TEAM 1
# Purpose Details: Encryption Function for the RSA team assignment
# Course: IST440W
# Author: VALERIE MALICKA
# Date Developed: 10/18/2025
# Last Date Changed: 10/21/2025
# Revision: Some revisions needed to be done. Using the code that was givven to us in class to help with understanding of RSA.

import random
import math

# helpers
def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    r = int(n**0.5)
    for i in range(3, r+1, 2):
        if n % i == 0:
            return False
    return True

def egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def modinv(a, m):
    a = a % m
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m

# key generation (simple)
def generate_keys(use_example=False):
    if use_example:
        p, q = 61, 53
        n = p * q
        phi = (p - 1) * (q - 1)
        e = 17
        d = modinv(e, phi)
        return ((e, n), (d, n), (p, q))

    primes = [p for p in range(50, 150) if is_prime(p)]
    p = random.choice(primes)
    q = random.choice([x for x in primes if x != p])
    n = p * q
    phi = (p - 1) * (q - 1)
    e = random.choice([x for x in range(3, phi, 2) if math.gcd(x, phi) == 1])
    d = modinv(e, phi)
    return ((e, n), (d, n), (p, q))

# encrypt/decrypt
def encrypt(message, public_key):
    e, n = public_key
    return [pow(ord(char), e, n) for char in message]

def decrypt(ciphertext, private_key):
    d, n = private_key
    return ''.join([chr(pow(c, d, n)) for c in ciphertext])

# test (uses professor example)
if __name__ == "__main__":
    public_key, private_key, (p, q) = generate_keys(use_example=True)
    print("Public Key:", public_key)
    print("Private Key:", private_key)
    print(f"Primes used: p = {p}, q = {q}")

    message = "HELLO"
    ciphertext = encrypt(message, public_key)
    print("\nOriginal Message:", message)
    print("Encrypted:", ciphertext)

    plaintext = decrypt(ciphertext, private_key)
    print("Decrypted:", plaintext)
