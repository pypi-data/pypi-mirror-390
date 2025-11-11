"""
bioconverter - Universal Bioinformatics Data Converter

A comprehensive toolkit for converting various bioinformatics data formats
to unified standard formats. Supports genomics (GWAS, VCF), transcriptomics
(RNA-seq), proteomics, and metabolomics data.
"""

__version__ = "0.1.2"

# Import main modules for easier access
from .convertor import (
    convert_single_file,
    convert_multiple_files,
    read_data,
    read_vcf_file,
    match_columns,
    create_genetic_column_patterns,
)

from .interactive_converter import (
    auto_suggest_mapping,
    auto_detect_omics_type,
    interactive_column_mapping,
    process_large_file,
    suggest_chunk_size,
)

from .conversion_report import ConversionReport

__all__ = [
    # Main conversion functions
    "convert_single_file",
    "convert_multiple_files",
    "read_data",
    "read_vcf_file",
    "match_columns",
    "create_genetic_column_patterns",
    # Interactive functions
    "auto_suggest_mapping",
    "auto_detect_omics_type",
    "interactive_column_mapping",
    "process_large_file",
    "suggest_chunk_size",
    # Report class
    "ConversionReport",
]
