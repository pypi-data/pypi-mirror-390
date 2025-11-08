#!/usr/bin/env python3
"""
Setup script for kanban task manager.

This package provides a shell-based kanban task manager with NDJSON storage,
high-performance search, and LLM-optimized interface.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    """Read README.md for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "A shell-based kanban task manager with NDJSON storage and high-performance search."

# Read requirements
def read_requirements():
    """Read requirements.txt for dependencies."""
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="juno-kanban",
    version="1.17.0",
    author="Juno AI",
    author_email="support@juno.ai",
    description="A shell-based kanban task manager with NDJSON storage and high-performance search",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/askbudi/feedback-shell",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "juno-kanban=kanban.cli:main",
            "juno-feedback=kanban.cli:main",
            "kanban-juno=kanban.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "kanban": ["*.json", "*.md"],
    },
    project_urls={
        "Bug Reports": "https://github.com/askbudi/feedback-shell/issues",
        "Source": "https://github.com/askbudi/feedback-shell",
        "Documentation": "https://github.com/askbudi/feedback-shell#readme",
    },
    keywords="kanban task-manager cli ndjson productivity",
    zip_safe=False,
)