from setuptools import setup, find_packages
from pathlib import Path

# Read README.md for long_description
this_directory = Path(__file__).parent
long_description = ""
readme_file = this_directory / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="ghostguard",           # PyPI package name
    version="1.6",               # updated version
    description="GhostGuard CLI — AI-powered Smart Corrector and Talk Assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Souparno Goswami",
    packages=find_packages(),    # will correctly find ghostguard folder
    python_requires=">=3.8",
    install_requires=[
        "pyfiglet",
        "colorama",
        "python-dotenv",
        "google-genai",
        "pyttsx3",
        "pyreadline3"
    ],
    entry_points={
        "console_scripts": [
            "ghost=ghostguard.cli:main",  # CLI command points to folder/module
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries",
    ],
)
