# ABCapstoneFA25Team1

---

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

---
