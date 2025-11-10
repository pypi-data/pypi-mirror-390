#!/usr/bin/env python3
"""
Setup configuration for DeepSeek R1 Local Web UI
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="deepseek-r1-local",
    version="1.0.0",
    author="DeepSeek R1 Local Team",
    author_email="contact@example.com",
    description="Offline AI Web UI with Council Deliberation System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/deepseek-r1-local",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "torch>=2.1.0",
        "transformers>=4.36.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "duckduckgo-search>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "deepseek-r1-local=deepseek_r1_local.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "deepseek_r1_local": ["templates/*.html", "static/*"],
    },
)
