# ABCapstoneFA25Team1

---

## Course Information
- CMPSC 488: Capstone Project Quantum Cryptosystem
- Penn State Abington
- Fall 2025

## Team and Members
- Robert Jajko
- Avik Bhuiyan
- Aaron Polite
- Valerie Malicka
- Huy Nguyen
- Kamilla Anarkulova
- Shakhzoda Ziyadullaeva

## Technologies Used
- Python 3
- Poetry
- Qiskit

## Project Overview
We aim to develop a CLI and GUI application that allows users to encrypt files using the RSA cryptosystem and decrypt them using a qiskit implementation of Shor's algorithm.

## Project Objectives
For this project our main objective is to develop a robust implementation of Shor's algorithm using qiskit that can generalize to an arbitrary N value while still maintaining reasonable performance.

## Project Structure

```
abcapstonefa25team1/
├── abcapstonefa25team1/
│   ├── __init__.py
│   ├── main.py                   # Unified initialization logic
    ├── utils/
│   ├── frontend/
│   │   ├── cli/
│   │   │   └── app.py            # CLI entry
│   │   └── gui/
│   │       └── app.py            # GUI entry
│   └── backend/
│       ├── rsa/
│       │   └── __init__.py
│       └── quantum/
│           └── __init__.py
├── pyproject.toml
├── poetry.lock
└── README.md
```

---

## Installation

This project uses **Poetry** for dependency management and environment isolation.

NOTE: **Make sure Poetry is installed**
   ```bash
   pip install poetry
   ```

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/abcapstonefa25team1.git
   cd abcapstonefa25team1
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

---

## Running the Project

The project defines multiple **entry points** using Poetry’s `scripts` feature.

### Run the CLI version
```bash
poetry run cli
```

### Run the GUI version
```bash
poetry run gui
```
### Run the pytest
```bash
poetry run pytest -v
```

---


## CLI Documentation

To view all available commands and options:
```bash
poetry run cli --help
```

Global options:
```bash
Short              Long           Description
-h                 --help       Show help message and exit
-d                 --debug      Enable detailed debugging logs
-v                 --verbose    Display verbose runtime messages
```


Encrypt a plaintext file using the RSA public key or generates a new keypair
```bash
poetry run cli encrypt INPUT [-o OUTPUT] [-k e n]
```
Options
```bash
Short       Long          Type       Default           Description
-o          --output      str        stdout          Output encrypted file
-k          --keys       int int     [7,143]        Public RSA key pair (e,n)
```

Example
```bash
# Encrypt using default public key
poetry run cli encrypt <file name> -o <file name>.enc

# Encrypt with custom RSA key
poetry run cli encrypt <file name> -k 11 221 -o <file name>.enc
```


Decrypts an encrypted file using either classical or quantum Shor’s algorithm to factor the RSA modulus.
```bash
poetry run cli decrypt INPUT [-o OUTPUT] [-c] [-e E] [-m N]
```
Options
```bash
Short        Long           Type            Default           Description
-o         --output          str            stdout          Output plaintext
-c         --classical        -              False        Use classical Shor algorithm
-e         --exponent        int              7             Public exponent e
-m         --modules         int             143            Public modulus n
```
Examples
```bash
# Quantum Shor’s algorithm (default)
poetry run cli decrypt <file name>.enc -o <file name>.txt

# Classical Shor’s algorithm
poetry run cli decrypt <file name>.enc -c -m 187 -e 7
```

Logging
```bash
Flag        Level               Description
-v          INFO          Progress and key generation logs
-d          DEBUG       Detailed steps and Shor factoring output
```
Example
```bash
poetry run cli -d encrypt sample.txt
# 2025-11-10 20:35:02 - sred_cli - INFO - Encrypting using public key (e=7, n=143)
```

Example Workflow
```bash
# Encrypt a file
poetry run cli encrypt secret.txt -o secret.enc

# Decrypt using quantum Shor’s algorithm
poetry run cli decrypt secret.enc -o recovered.txt

# Verify file integrity
diff secret.txt recovered.txt
```
