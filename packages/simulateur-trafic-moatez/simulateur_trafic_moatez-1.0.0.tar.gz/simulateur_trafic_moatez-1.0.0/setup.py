#!/usr/bin/env python3
"""
Setup script pour le package simulateur-trafic utilisant setuptools.
"""

import os
from setuptools import setup, find_packages

# Lire le contenu du README pour la description longue
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Lire la version depuis __init__.py
def get_version():
    version_file = os.path.join("simulateur_trafic", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

setup(
    name="simulateur-trafic-moatez",
    version=get_version(),
    author="Moatez Tilouche",
    author_email="moateztilouch@gmail.com",
    description="Simulateur de trafic routier avec gestion d'exceptions et tests complets",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/MoatezTilouche/simulateur_trafic",
    project_urls={
        "Bug Tracker": "https://github.com/MoatezTilouche/simulateur_trafic/issues",
        "Documentation": "https://github.com/MoatezTilouche/simulateur_trafic",
        "Source Code": "https://github.com/MoatezTilouche/simulateur_trafic",
    },
    packages=find_packages(exclude=["tests*", "junit-tests*", "docs*"]),
    package_data={
        "simulateur_trafic": [
            "data/*.json",
            "data/*.csv",
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="traffic simulation simulator transport routing",
    python_requires=">=3.8",
    install_requires=[
        # Aucune dépendance externe requise
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "build",
            "twine",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov",
        ],
    },
    entry_points={
        "console_scripts": [
            "simulateur-trafic=simulateur_trafic.main:main",
        ],
    },
    zip_safe=False,
)