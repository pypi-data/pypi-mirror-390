# Bioinformatics Data Converter

A comprehensive and efficient tool for converting various bioinformatics data formats to a unified, standardized format. Designed to handle all types of omics data (genomics, transcriptomics, proteomics, metabolomics) and large files (gigabytes of data).

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

```bash
# Clone the repository
git clone https://github.com/Jeblqr/bioinformatic-data-converter.git
cd bioinformatic-data-converter

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Command-Line Interface

```bash
# Show file information only
python3 cli.py -i input_data.tsv --info-only

# Convert with auto-suggested mappings
python3 cli.py -i input_data.tsv -o output_data.tsv --auto-suggest

# Interactive column mapping
python3 cli.py -i input_data.csv -o output_data.tsv --interactive

# Batch interactive mode
python3 cli.py -i input_data.txt -o output_data.tsv --batch-interactive

# Manual column mapping
python3 cli.py -i input.txt -o output.tsv --map "CHR=chr,POS=pos,P_VALUE=pval"

# Process large file with chunking
python3 cli.py -i large_file.tsv.gz -o output.tsv --chunk-size 100000

# Show all supported column patterns
python3 cli.py --show-patterns
```

### Python API

```python
from convertor import convert_single_file
from interactive_converter import (
    interactive_column_mapping,
    process_large_file,
    auto_suggest_mapping
)

# Simple conversion with auto-detection
result = convert_single_file(
    filename="input_data.tsv",
    verbose=True
)

# Interactive column mapping
import pandas as pd
df = pd.read_csv("input_data.csv", nrows=1000)
suggested = auto_suggest_mapping(df)
mapping = interactive_column_mapping(df, suggested_mapping=suggested)

# Process large file efficiently
process_large_file(
    filename="large_data.tsv.gz",
    output_file="output.tsv",
    column_mapping=mapping,
    chunksize=100000,
    verbose=True
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
python3 cli.py -i gwas_data.tsv -o standardized_gwas.tsv --auto-suggest
```

Output `standardized_gwas.tsv.gz`:
```
chr  pos      rsid       alt  ref  beta    se      pval
1    10001    rs123456   A    G    0.05    0.02    0.001
1    20001    rs234567   C    T    -0.03   0.015   0.05
```

### Example 2: Transcriptomics RNA-seq Data

```bash
python3 cli.py -i rnaseq_results.csv -o standardized_rnaseq.tsv --auto-suggest --verbose
```

### Example 3: Large File Processing

```bash
# File is 5GB - automatically uses chunked processing
python3 cli.py -i huge_dataset.tsv.gz -o output.tsv --auto-suggest --verbose
```

### Example 4: Interactive Mapping

```bash
python3 cli.py -i custom_format.txt -o output.tsv --interactive
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
from interactive_converter import create_omics_column_patterns

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
from convertor import convert_multiple_files

files = ['file1.tsv', 'file2.csv', 'file3.vcf.gz']
results = convert_multiple_files(
    file_list=files,
    keep_unmatched=False,
    verbose=True
)

# Combine results
import pandas as pd
combined = pd.concat(results.values(), ignore_index=True)
```

### Memory-Efficient Processing

```python
from interactive_converter import suggest_chunk_size, process_large_file

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

## CLI Reference

```
usage: cli.py [-h] -i INPUT [-o OUTPUT] [--sep SEP]
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
  --auto-suggest                Use auto-suggested mappings
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

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source and available for use in bioinformatics research and applications.
