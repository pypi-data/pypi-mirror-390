"""
Setup script for Trello CLI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="trello-cli-python",
    version="2.1.12",
    author="Bernard Uriza Orozco",
    author_email="bernard@example.com",
    description="Official Python CLI for Trello - Optimized for agile workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bernardurizaorozco/trello-cli-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "py-trello>=0.19.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "trello-cli=trello_cli.cli:main",
        ],
    },
    scripts=["trello"],
    include_package_data=True,
)
