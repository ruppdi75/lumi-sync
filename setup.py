#!/usr/bin/env python3
"""
LumiSync - Linux Settings Synchronization Tool
Setup script for installation and packaging
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="lumisync",
    version="0.2.0",
    author="LumiSync Development Team",
    author_email="dev@lumisync.org",
    description="Synchronize your Linux desktop settings across devices",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/lumisync/lumisync",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "lumisync=lumisync.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "lumisync": [
            "assets/*",
            "config/*.json",
            "gui/themes/*.qss",
        ],
    },
    keywords="linux desktop synchronization settings backup restore",
    project_urls={
        "Bug Reports": "https://github.com/lumisync/lumisync/issues",
        "Source": "https://github.com/lumisync/lumisync",
        "Documentation": "https://docs.lumisync.org",
    },
)
