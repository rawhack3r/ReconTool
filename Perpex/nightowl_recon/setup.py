#!/usr/bin/env python3
"""
Setup script for NightOwl Enhanced Reconnaissance Suite
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="nightowl-recon",
    version="2.0.0",
    description="Enhanced reconnaissance automation tool with AI integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="n00bhack3r",
    author_email="contact@nightowl-recon.com",
    url="https://github.com/yourusername/nightowl-recon",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'nightowl=main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
    ],
    keywords="reconnaissance security pentesting bugbounty osint",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/nightowl-recon/issues",
        "Source": "https://github.com/yourusername/nightowl-recon",
        "Documentation": "https://nightowl-recon.readthedocs.io/",
    },
    package_data={
        'nightowl_recon': [
            'data/wordlists/*.txt',
            'data/patterns/*.json',
            'data/configs/*.json',
            'reporting/templates/*.html',
        ],
    },
    zip_safe=False,
)
