import os

def create_gitignore():
    """Creates a basic .gitignore file if it does not exist."""

    if not os.path.exists(".gitignore"):
        with open(".gitignore", "w") as f:
            f.write("""# Python-specific ignores
__pycache__/
*.pyc
*.pyo
*.pyd
.venv/
data/
.env
""")
    else:
        print(".gitignore already exists.")

def create_readme():
    """Creates a basic README.md file."""

    if os.path.exists("README.md"):
        overwrite = input("README.md already exists. Do you want to overwrite it? (y/n): ")
        if overwrite.lower() != 'y':
            print("README.md not overwritten.")
            return

    with open("README.md", "w") as f:
        f.write("""# Project Title
## My package
Description of your package.
## Overview
Overview of your project.
## Author(s)
List of authors.
## Usage
Instructions on how to use your project.
```python3
>>> import mypackage
>>> mypackage.do_stuff()
```
            
## Installation
Instructions on how to install your project.
""")

def create_venv():
    """Creates a virtual environment."""

    os.system("python3 -m venv .venv")

def create_requirements():
    """Creates a requirements.txt file."""

    with open("requirements.txt", "w") as f:
        f.write("""# List of dependencies
ipython
ipykernel
numpy
pandas
matplotlib
seaborn
scipy
statsmodels
""")

if __name__ == "__main__":
    create_gitignore()
    create_readme()
    create_venv()
    create_requirements()
    print("Files created: .gitignore, README.md, requirements.txt")
    print("Virtual environment created: .venv")
    print("next step is: source .venv/bin/activate")
    print("then: pip install -r requirements.txt")
