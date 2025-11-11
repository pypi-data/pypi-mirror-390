# bioconverter

[![PyPI version](https://img.shields.io/pypi/v/bioconverter.svg)](https://pypi.org/project/bioconverter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A comprehensive and efficient tool for converting various bioinformatics data formats to a unified, standardized format. Designed to handle all types of omics data (genomics, transcriptomics, proteomics, metabolomics) and large files (gigabytes of data).

**PyPI**: https://pypi.org/project/bioconverter/  
**GitHub**: https://github.com/Jeblqr/bioConv

## Features

### 🔄 Universal Data Format Conversion

- **Multi-omics Support**: Genomics, transcriptomics, proteomics, and metabolomics data
- **Format Detection**: Automatic detection of file formats (CSV, TSV, VCF, compressed files)
- **Intelligent Mapping**: Auto-detection and mapping of column names to standardized format
- **Flexible Input**: Supports various separators, compression formats (gzip, bz2, zip, xz), and comment characters

### 💡 Interactive Column Renaming

- **Interactive Mode**: Step-by-step column mapping with suggestions
- **Batch Interactive Mode**: Enter all mappings at once
- **Auto-Suggest Mode**: Fully automated column mapping based on recognized patterns
- **Manual Mapping**: Explicit column mapping for complete control
- **Preview & Confirm**: Review mappings before processing

### 🚀 Large File Handling

- **Chunked Processing**: Efficiently processes gigabyte-sized files
- **Memory Management**: Automatic chunk size suggestion based on file size
- **Streaming Output**: Writes output incrementally to avoid memory issues
- **Progress Tracking**: Real-time progress updates for large file processing

### 📊 Supported Data Types

#### Genomics

- GWAS summary statistics
- VCF files (variant call format)
- SNP data
- Association study results

#### Transcriptomics

- RNA-seq count data
- FPKM/TPM expression values
- Differential expression results
- Gene expression matrices

#### Proteomics

- Protein abundance data
- Peptide intensity measurements
- Quantitative proteomics results

#### Metabolomics

- Metabolite concentrations
- LC-MS/GC-MS peak data
- Metabolite identification results

## Installation

### Python Package (Recommended)

```bash
# Install from PyPI
pip install bioconverter

# Or install from GitHub (latest version)
pip install git+https://github.com/Jeblqr/bioConv.git
```

### R Package

```r
# Install from GitHub
remotes::install_github("Jeblqr/bioConv")

# Install dependencies
install.packages(c("reticulate", "tibble", "readr"))

# Install Python bioconverter package
reticulate::py_install("bioconverter", pip = TRUE)
```

### Verify Installation

```bash
# Python
python -c "from bioconverter import convertor; print('bioconverter installed!')"

# CLI
bioconverter --help
```

```r
# R
library(bioconverter)
```

## Quick Start

### Command-Line Interface (CLI)

```bash
# Show file information only
bioconverter -i input_data.tsv --info-only

# Convert with auto-suggested mappings (recommended)
bioconverter -i input_data.tsv -o output_data.tsv --auto-suggest

# Interactive column mapping
bioconverter -i input_data.csv -o output_data.tsv --interactive

# Manual column mapping
bioconverter -i input.txt -o output.tsv --map "CHR=chr,POS=pos,P_VALUE=pval"

# Process large file with automatic chunking
bioconverter -i large_file.tsv.gz -o output.tsv --auto-suggest

# Show all supported column patterns
bioconverter --show-patterns
```

### Python API

```python
from bioconverter.convertor import convert_single_file
from bioconverter.interactive_converter import (
    auto_suggest_mapping,
    process_large_file
)

# Simple conversion with auto-detection
result = convert_single_file(
    filename="input_data.tsv",
    verbose=True
)

# Auto-suggest mapping
import pandas as pd
df = pd.read_csv("input_data.csv", nrows=1000)
mapping = auto_suggest_mapping(df)

# Apply mapping and convert
result = convert_single_file(
    filename="input_data.csv",
    column_mapping=mapping,
    verbose=True
)

# Process large file efficiently
process_large_file(
    filename="large_data.tsv.gz",
    output_file="output.tsv",
    column_mapping=mapping,
    chunksize=100000,
    verbose=True
)
```

### R Interface

```r
library(bioconverter)

# Basic conversion
result <- convert_file(
  input_file = "input_data.tsv",
  output_file = "output_data.tsv",
  verbose = TRUE
)

# Auto-suggest mapping
suggestions <- auto_suggest_mapping("input_data.tsv", n_rows = 1000)

# Apply suggested mapping
result <- convert_file(
  input_file = "input_data.tsv",
  output_file = "output_data.tsv",
  column_mapping = suggestions
)
```

## Usage Examples

### Example 1: Genomics GWAS Data

Input file `gwas_data.tsv`:

```
CHR  POS      SNP        A1  A2  BETA    SE      P
1    10001    rs123456   A   G   0.05    0.02    0.001
1    20001    rs234567   C   T   -0.03   0.015   0.05
```

Convert:

```bash
bioconverter -i gwas_data.tsv -o standardized_gwas.tsv --auto-suggest
```

Output `standardized_gwas.tsv.gz`:

```
chr  pos      rsid       alt  ref  beta    se      pval
1    10001    rs123456   A    G    0.05    0.02    0.001
1    20001    rs234567   C    T    -0.03   0.015   0.05
```

### Example 2: Transcriptomics RNA-seq Data

```bash
bioconverter -i rnaseq_results.csv -o standardized_rnaseq.tsv --auto-suggest --verbose
```

### Example 3: Large File Processing

```bash
# File is 5GB - automatically uses chunked processing
bioconverter -i huge_dataset.tsv.gz -o output.tsv --auto-suggest --verbose
```

### Example 4: Interactive Mapping

```bash
bioconverter -i custom_format.txt -o output.tsv --interactive
```

This will prompt you for each column:

```
Original columns found:
  1. Chromosome [identifier]
  2. Position [numeric]
  3. P-value [probability/score]
  ...

For each column, enter the standard name (or press Enter to skip)
Chromosome -> chr
Position -> pos
P-value -> pval
...
```

## Standardized Column Names

### Genomics Fields

- `chr`: Chromosome
- `pos`: Position
- `rsid`: SNP/variant identifier
- `ref`: Reference allele
- `alt`: Alternate/effect allele
- `pval`: P-value
- `beta`: Effect size
- `se`: Standard error
- `or`: Odds ratio
- `frq`: Allele frequency
- `n`: Sample size
- `info`: Imputation quality

### Transcriptomics Fields

- `gene_id`: Gene identifier (e.g., ENSG)
- `gene_name`: Gene symbol
- `transcript_id`: Transcript identifier
- `expression`: Expression value
- `fpkm`: FPKM value
- `tpm`: TPM value
- `counts`: Read counts
- `log2fc`: Log2 fold change
- `padj`: Adjusted p-value

### Proteomics Fields

- `protein_id`: Protein identifier
- `protein_name`: Protein name
- `peptide`: Peptide sequence
- `abundance`: Protein abundance
- `intensity`: Signal intensity
- `ratio`: Fold change ratio

### Metabolomics Fields

- `metabolite_id`: Metabolite identifier
- `metabolite_name`: Metabolite name
- `mz`: Mass-to-charge ratio
- `rt`: Retention time
- `concentration`: Concentration
- `peak_area`: Peak area

### Sample Information

- `sample_id`: Sample identifier
- `condition`: Experimental condition
- `timepoint`: Time point
- `replicate`: Replicate number
- `batch`: Batch identifier

## Advanced Features

### Custom Pattern Matching

```python
import re
from bioconverter.convertor import convert_single_file

# Add custom patterns
custom_patterns = {
    'my_field': re.compile(r'^(myfield|my_field|custom_name)$', re.IGNORECASE)
}

# Use in conversion
result = convert_single_file(
    filename="data.tsv",
    custom_patterns=custom_patterns
)
```

### Batch Processing Multiple Files

```python
from bioconverter.convertor import convert_multiple_files
import pandas as pd

files = ['file1.tsv', 'file2.csv', 'file3.vcf.gz']
results = convert_multiple_files(
    file_list=files,
    keep_unmatched=False,
    verbose=True
)

# Combine results
combined = pd.concat(results.values(), ignore_index=True)
```

### Memory-Efficient Processing

```python
from bioconverter.interactive_converter import suggest_chunk_size, process_large_file

# Automatically determine chunk size
chunk_size = suggest_chunk_size("huge_file.tsv", available_memory_gb=8.0)

# Process with optimal chunk size
process_large_file(
    filename="huge_file.tsv",
    output_file="output.tsv",
    column_mapping=your_mapping,
    chunksize=chunk_size
)
```

## File Format Support

### Input Formats

- **Plain text**: `.txt`, `.tsv`, `.csv`
- **Compressed**: `.gz`, `.bz2`, `.zip`, `.xz`
- **Specialized**: `.vcf`, `.vcf.gz`
- **Auto-detection**: Format automatically detected from extension

### Output Formats

- **TSV** (tab-separated, default)
- **CSV** (comma-separated)
- **Parquet** (columnar format)
- **Compression**: gzip by default (can be disabled with `--no-compression`)

## Complete Examples

See the `examples/` directory for complete working examples:

- **Python**: `examples/example_python.py` - Comprehensive Python API examples
- **R**: `examples/example_r.R` - Complete R interface examples
- **Bash/CLI**: `examples/example_bash.sh` - Shell scripting examples

Run them:

```bash
# Python
python examples/example_python.py

# R
Rscript examples/example_r.R

# Bash
bash examples/example_bash.sh
```

## CLI Reference

```
usage: bioconverter [-h] -i INPUT [-o OUTPUT] [--sep SEP]
                    [--compression {gzip,bz2,zip,xz}] [--comment COMMENT] [--vcf]
                    [--interactive | --batch-interactive | --auto-suggest | --map MAP]
                    [--chunk-size CHUNK_SIZE] [--memory MEMORY] [--keep-unmatched]
                    [--output-format {csv,tsv,parquet}] [--no-compression]
                    [--info-only] [--preview PREVIEW] [--verbose] [--show-patterns]

Options:
  -i INPUT, --input INPUT       Input file path
  -o OUTPUT, --output OUTPUT    Output file path
  --sep SEP                     Column separator
  --compression {gzip,bz2,zip,xz}  Compression format
  --vcf                         Treat as VCF format
  --interactive                 Interactive column mapping
  --batch-interactive           Batch interactive mode
  --auto-suggest                Use auto-suggested mappings (recommended)
  --map MAP                     Manual mapping (e.g., "old1=new1,old2=new2")
  --chunk-size CHUNK_SIZE       Chunk size for large files
  --memory MEMORY               Available memory in GB
  --keep-unmatched              Keep unmapped columns
  --output-format {csv,tsv,parquet}  Output format
  --no-compression              Disable output compression
  --info-only                   Show file info only
  --verbose                     Verbose output
  --show-patterns               Show supported patterns
```

## Performance

- **Small files (<100MB)**: Processed in memory, very fast
- **Medium files (100MB-1GB)**: Chunked processing with 200K row chunks
- **Large files (1-10GB)**: Chunked processing with 100K row chunks
- **Very large files (>10GB)**: Chunked processing with 50K row chunks

Memory usage is optimized to stay under 4GB by default (configurable).

## Documentation

- **Complete Usage Guide**: [USAGE.md](USAGE.md) - Detailed documentation with examples
- **PyPI Package**: https://pypi.org/project/bioconverter/
- **GitHub Repository**: https://github.com/Jeblqr/bioConv
- **Issue Tracker**: https://github.com/Jeblqr/bioConv/issues

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Citation

If you use bioconverter in your research, please cite:

```bibtex
@software{bioconverter2025,
  title = {bioconverter: Universal Bioinformatics Data Converter},
  author = {Bioinformatics Data Converter Contributors},
  year = {2025},
  url = {https://github.com/Jeblqr/bioConv},
  version = {0.1.2}
}
```

## License

MIT License - Free for academic research and commercial applications.

## Support

- **Issues**: https://github.com/Jeblqr/bioConv/issues
- **Discussions**: https://github.com/Jeblqr/bioConv/discussions
