# -*- coding: utf-8 -*-
"""
Setup configuration for proyecto_mlops package.
"""

import os
from setuptools import setup, find_packages

# Read README from root directory
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
with open(readme_path, "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="proyecto-mlops",
    version="0.1.0",
    author="Angel Castillo",
    author_email="angelcast2002@gmail.com",
    description="MLOps Pipeline para Clasificación de Documentos en Español",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/angelcast2002/PROYECTO-MLOPS",
    project_urls={
        "Bug Tracker": "https://github.com/angelcast2002/PROYECTO-MLOPS/issues",
        "Documentation": "https://github.com/angelcast2002/PROYECTO-MLOPS/wiki",
        "Source Code": "https://github.com/angelcast2002/PROYECTO-MLOPS",
    },
    packages=find_packages(exclude=["tests", "docs_project", "infra", "config"]),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.20.0",
        "scikit-learn>=1.0.0",
        "nltk>=3.8",
        "gensim>=4.0.0",
        "spacy>=3.0.0",
        "typer[all]>=0.9.0",
        "pyyaml>=6.0",
        "joblib>=1.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "isort>=5.11.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "pylint>=2.13.0",
        ],
        "docker": [
            "gunicorn>=20.0.0",
            "uvicorn>=0.17.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "proyecto-mlops=proyecto_mlops.cli:main",
        ],
    },
    zip_safe=False,
)
