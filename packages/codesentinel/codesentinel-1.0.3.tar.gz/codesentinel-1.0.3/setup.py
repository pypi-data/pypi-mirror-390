#!/usr/bin/env python3
"""
CodeSentinel Setup Script
=========================

A Polymath Project | Created by joediggidyyy

Setup script for installing CodeSentinel as a Python package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README
this_directory = Path(__file__).parent
try:
    long_description = (this_directory / "README.md").read_text(encoding='utf-8')
except UnicodeDecodeError:
    # Fallback for encoding issues
    long_description = (this_directory / "README.md").read_text(encoding='utf-8', errors='ignore')

# Read version from package
def get_version():
    """Get version from package."""
    # Read version directly to avoid import issues during build
    return "1.0.3"

setup(
    name="codesentinel",
    version="1.0.3",  # Hardcoded to match pyproject.toml and __init__.py
    author="joediggidyyy",
    author_email="",
    description="Automated Maintenance & Security Monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joediggidyyy/CodeSentinel",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.13",
    install_requires=[
        "pathlib2>=2.3.0; python_version < '3.4'",
        "requests>=2.25.0",
        "schedule>=1.1.0",
        "psutil>=5.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "flake8>=3.8.0",
            "black>=21.0.0",
            "mypy>=0.800",
            "sphinx>=4.0.0",
        ],
        "gui": [
            # tkinter is included with Python, but can be specified for explicit installation
        ],
    },
    entry_points={
        "console_scripts": [
            "codesentinel=codesentinel.cli:main",
            "codesentinel-setup=codesentinel.launcher:main",
            "codesentinel-setup-gui=codesentinel.gui_launcher:main",  # Standalone dependency installer
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="security monitoring maintenance automation alerts",
    project_urls={
        "Bug Reports": "https://github.com/joediggidyyy/CodeSentinel/issues",
        "Source": "https://github.com/joediggidyyy/CodeSentinel",
        "Documentation": "https://codesentinel.readthedocs.io/",
    },
)