#!/usr/bin/env python3
import os
import sys
import subprocess
import time

# 🎨 ANSI Colors
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GRAY = "\033[90m"

# 🏗️ Project structure template
TEMPLATE = {
    "app": {
        "api": ["__init__.py", "routes.py"],
        "core": ["__init__.py", "config.py"],
        "models": ["__init__.py", "user.py"],
        "schemas": ["__init__.py", "user.py"],
        "db": ["__init__.py", "database.py"],
        "main.py": None,
    },
    "tests": ["test_main.py"],
    "requirements.txt": None,
    "README.md": None,
}

# 🧩 Base content of main.py
MAIN_TEMPLATE = """from fastapi import FastAPI

app = FastAPI(title="FastAPI Starter")

@app.get("/")
def read_root():
    return {"message": "🚀 Hello from FastAPI!"}
"""

# 📖 Base content of README.md
README_TEMPLATE = """# FastAPI Starter Project

This is a base project to start applications with FastAPI, a modern and fast framework for building APIs with Python.

## Project Description

This project provides a modular and organized structure for developing web applications with FastAPI. It includes basic configuration, data models, schemas, API routes, and an integrated database.

## Folder Architecture

```
project/
├── app/
│   ├── api/          # API routes and endpoints
│   ├── core/         # Central configuration (config.py)
│   ├── models/       # Data models (ORM)
│   ├── schemas/      # Pydantic schemas for validation
│   ├── db/           # Database configuration
│   └── main.py       # Application entry point
├── tests/            # Unit and integration tests
├── requirements.txt  # Project dependencies
└── README.md         # This file
```

## Installation and Usage

1. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```
   uvicorn app.main:app --reload
   ```

## Deployment

To deploy in production:

1. Install Gunicorn for WSGI server:
   ```
   pip install gunicorn
   ```

2. Run with Gunicorn:
   ```
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

3. Optionally, configure a reverse proxy with Nginx.

## Adding Dependencies

To add new dependencies to the project:

1. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

2. Install the new dependency:
   ```
   pip install <package_name>
   ```

3. Update the requirements.txt file:
   ```
   pip freeze > requirements.txt
   ```

4. Commit the changes in Git:
   ```
   git add requirements.txt
   git commit -m "Add new dependency: <package_name>"
   ```
"""

# 🧱 Create structure recursively
def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        elif isinstance(content, list):
            os.makedirs(path, exist_ok=True)
            for file_name in content:
                open(os.path.join(path, file_name), "w", encoding="utf-8").close()
        else:
            open(path, "w", encoding="utf-8").close()

# 💬 Small delay for visual effect
def wait(msg):
    print(Color.GRAY + msg + Color.RESET)
    time.sleep(0.5)

def main():
    if len(sys.argv) < 2:
        print(Color.RED + "❌ Usage: mkf <project_name>" + Color.RESET)
        sys.exit(1)

    project_name = sys.argv[1]
    base_path = os.path.abspath(project_name)

    if os.path.exists(base_path):
        print(Color.YELLOW + f"⚠️  The directory '{project_name}' already exists." + Color.RESET)
        sys.exit(1)

    print(f"\n{Color.CYAN}{Color.BOLD}✨ Creating FastAPI project: {project_name}{Color.RESET}\n")

    wait("📁 Generating folder structure...")
    os.makedirs(base_path)
    create_structure(base_path, TEMPLATE)

    wait("🧩 Adding base files...")
    # Open in binary and write UTF-8 bytes to avoid platform encoding issues
    # (e.g. Windows cp1252 can't encode emoji). Writing bytes is robust
    # regardless of the system locale.
    with open(os.path.join(base_path, "app", "main.py"), "wb") as f:
        f.write(MAIN_TEMPLATE.encode("utf-8"))

    with open(os.path.join(base_path, "README.md"), "wb") as f:
        f.write(README_TEMPLATE.encode("utf-8"))

    wait("🐍 Creating virtual environment...")
    subprocess.run(["python3", "-m", "venv", os.path.join(base_path, ".venv")])

    wait("📦 Installing main dependencies (FastAPI + Uvicorn)...")
    pip_path = os.path.join(base_path, ".venv", "bin", "pip")
    subprocess.run([pip_path, "install", "--upgrade", "pip"], stdout=subprocess.DEVNULL)
    subprocess.run([pip_path, "install", "fastapi", "uvicorn"], stdout=subprocess.DEVNULL)

    wait("📝 Generating requirements.txt...")
    # Write requirements in binary so subprocess output (bytes) is written
    # directly and no text-encoding conversion happens.
    with open(os.path.join(base_path, "requirements.txt"), "wb") as f:
        subprocess.run([pip_path, "freeze"], stdout=f)

    wait("🗃️  Initializing Git repository...")
    subprocess.run(["git", "init", base_path], stdout=subprocess.DEVNULL)
    subprocess.run(["git", "-C", base_path, "add", "."], stdout=subprocess.DEVNULL)
    subprocess.run(["git", "-C", base_path, "commit", "-m", "Initial commit"], stdout=subprocess.DEVNULL)

    print(f"\n{Color.GREEN}✅ Project '{project_name}' created successfully!{Color.RESET}")
    print(f"{Color.CYAN}📦 Virtual environment:{Color.RESET} {base_path}/.venv")
    print(f"{Color.CYAN}🚀 To start the server:{Color.RESET}")
    print(f"   {Color.YELLOW}cd {project_name}{Color.RESET}")
    print(f"   {Color.YELLOW}source .venv/bin/activate{Color.RESET}")
    print(f"   {Color.YELLOW}uvicorn app.main:app --reload{Color.RESET}\n")

    print(f"{Color.GRAY}Done!{Color.RESET}\n")

if __name__ == "__main__":
    main()

