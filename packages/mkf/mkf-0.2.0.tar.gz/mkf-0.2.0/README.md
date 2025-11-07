# mkf

A simple CLI tool to generate FastAPI starter projects with a modular structure.

## Installation

Install via pip:
```bash
pip install mkf
```

Or install from source:

1. Clone this repository:
   ```bash
   git clone <repo_url>
   cd mkf
   ```

2. Install the package:
   ```bash
   pip install .
   ```

## Usage

```bash
mkf <project_name>
```

Replace `<project_name>` with the name of your new FastAPI project.

## What it does

- Creates a directory with the project name
- Generates a modular folder structure for FastAPI
- Adds base files including main.py, models, schemas, etc.
- Sets up a Python virtual environment
- Installs FastAPI and Uvicorn
- Generates requirements.txt
- Initializes a Git repository with an initial commit

## Requirements

- Python 3.x
- pip
- git

## Example

```bash
./mkf my_fastapi_app
cd my_fastapi_app
source .venv/bin/activate
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs to see the interactive API documentation.

## Project Structure

The generated project has the following structure:

```
project_name/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   └── main.py
├── tests/
│   └── test_main.py
├── .venv/          # Virtual environment
├── requirements.txt
├── README.md
└── .git/           # Git repository
```

## License

MIT