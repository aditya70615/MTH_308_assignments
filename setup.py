# setup.py ────────────────────────────────────────────────────────────────
from pathlib import Path
from setuptools import setup, find_packages

# Read long description from README.md
this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="mth308lib",                         # ← UNIQUE on PyPI
    version="0.1.0",                         # ↑ bump for every new release
    description="Numerical-methods library for MTH308 with CLI support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Aditya Singh",
    author_email="your.email@example.com",
    url="https://github.com/aditya70615/MTH_308_assignments",
    packages=find_packages(),                # finds the mth308/ package
    py_modules=["cli"],                      # include cli.py at top level
    entry_points={                           # exposes the terminal command
        "console_scripts": [
            "mth308=cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
