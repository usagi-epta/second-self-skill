#!/usr/bin/env python3
"""
Setup script for Recursive Self-Evolution package
"""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README_IMPLEMENTATION.md").read_text()

setup(
    name="recursive-self-evolution",
    version="3.0.0",
    author="usagi.epta",
    author_email="null@example.com",
    description="Recursive Self-Definition architecture for persistent LLM agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/usagi-epta/second-self-skill",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies (minimal)
        "dataclasses;python_version<'3.7'",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "ollama": ["ollama>=0.1.0"],
        "langchain": ["langchain>=0.1.0"],
        "all": [
            "openai>=1.0.0",
            "ollama>=0.1.0",
            "langchain>=0.1.0",
            "requests>=2.25.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "recursive-agent=cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
