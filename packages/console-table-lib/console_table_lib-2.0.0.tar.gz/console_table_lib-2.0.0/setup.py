"""
Setup configuration for Console Table Library
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read version from package
version = {}
with open("console_table/__init__.py", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            exec(line, version)
            break

setup(
    name="console-table-lib",
    version=version.get("__version__", "2.0.0"),
    author="Your Name",
    author_email="your.email@example.com",
    description="Eine umfassende und dennoch verdammt einfache Python-Bibliothek zur Erstellung von gut formatierten Tabellen in der Konsole",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/console-table",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "rich>=13.0.0",
        "pandas>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    keywords="console table terminal cli formatting display rich pandas",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/console-table/issues",
        "Source": "https://github.com/yourusername/console-table",
        "Documentation": "https://github.com/yourusername/console-table#readme",
    },
)

