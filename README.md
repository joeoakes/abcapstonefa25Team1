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
