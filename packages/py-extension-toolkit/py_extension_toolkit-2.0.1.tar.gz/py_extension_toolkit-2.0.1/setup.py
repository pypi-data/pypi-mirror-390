#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="project-manager-cli",
    version="2.0.1",
    author="AQARY INTERNATIONAL GROUP",
    author_email="thamjid@aqaryint.com",
    description="A CLI tool for managing projects and apps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aqary-Org/py-extension-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "project-mgr=project_manager_cli.main:main",
        ],
    },
    install_requires=[
        # Add any dependencies here if needed
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
)