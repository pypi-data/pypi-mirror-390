"""
Setup script for bioinformatic-data-converter Python package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="bioconverter",
    version="0.1.0",
    author="Bioinformatics Data Converter Contributors",
    author_email="",
    description="Universal bioinformatics data converter for multi-omics data formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jeblqr/bioinformatic-data-converter",
    packages=find_packages(exclude=["tests", "test_data"]),
    py_modules=[
        "convertor",
        "interactive_converter",
        "conversion_report",
        "cli"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "pyarrow>=12.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bioconverter=cli:main",
        ],
    },
    keywords="bioinformatics genomics transcriptomics proteomics metabolomics data-conversion",
    project_urls={
        "Bug Reports": "https://github.com/Jeblqr/bioinformatic-data-converter/issues",
        "Source": "https://github.com/Jeblqr/bioinformatic-data-converter",
        "Documentation": "https://github.com/Jeblqr/bioinformatic-data-converter/blob/main/README.md",
    },
)
