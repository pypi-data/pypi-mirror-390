"""
Interactive Bioinformatics Data Converter
Provides interactive column renaming and handles large files efficiently
"""

import pandas as pd
import re
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import sys


def detect_column_types(df: pd.DataFrame, sample_size: int = 1000) -> Dict[str, str]:
    """
    Automatically detect the type and purpose of columns by analyzing content.
    
    Args:
        df: DataFrame to analyze
        sample_size: Number of rows to sample for analysis
        
    Returns:
        Dictionary mapping column names to detected types
    """
    column_types = {}
    sample_df = df.head(sample_size)
    
    for col in df.columns:
        col_data = sample_df[col].dropna()
        
        if len(col_data) == 0:
            column_types[col] = "unknown"
            continue
            
        # Check for numeric data
        try:
            pd.to_numeric(col_data)
            # Check if it looks like p-values (between 0 and 1)
            numeric_data = pd.to_numeric(col_data, errors='coerce')
            if (numeric_data >= 0).all() and (numeric_data <= 1).all():
                column_types[col] = "probability/score"
            else:
                column_types[col] = "numeric"
        except:
            # Check for categorical/identifier data
            unique_ratio = len(col_data.unique()) / len(col_data)
            if unique_ratio > 0.9:
                column_types[col] = "identifier"
            else:
                column_types[col] = "categorical"
                
    return column_types


def interactive_column_mapping(
    df: pd.DataFrame,
    suggested_mapping: Optional[Dict[str, str]] = None,
    batch_mode: bool = False
) -> Dict[str, str]:
    """
    Interactively ask user to map column names to standardized names.
    
    Args:
        df: DataFrame with columns to map
        suggested_mapping: Pre-suggested mappings based on pattern matching
        batch_mode: If True, show all suggestions at once
        
    Returns:
        Dictionary mapping original column names to standardized names
    """
    print("\n" + "="*80)
    print("INTERACTIVE COLUMN MAPPING")
    print("="*80)
    print("\nOriginal columns found:")
    
    # Detect column types
    column_types = detect_column_types(df)
    
    for i, col in enumerate(df.columns, 1):
        col_type = column_types.get(col, "unknown")
        suggested = suggested_mapping.get(col, "") if suggested_mapping else ""
        suggestion_str = f" (suggested: {suggested})" if suggested else ""
        print(f"  {i}. {col} [{col_type}]{suggestion_str}")
    
    print("\nAvailable standard column names:")
    print("  Identifiers: id, rsid, gene_id, protein_id, metabolite_id")
    print("  Genomic: chr, pos, ref, alt, a1, a2")
    print("  Expression: gene_name, gene_symbol, expression, fpkm, tpm, counts")
    print("  Protein: protein_name, abundance, intensity")
    print("  Metabolite: metabolite_name, concentration, peak_area")
    print("  Statistics: pval, beta, se, or, z, frq, n, info")
    print("  Sample: sample_id, condition, timepoint, replicate")
    
    if batch_mode:
        print("\n" + "-"*80)
        print("BATCH MAPPING MODE")
        print("-"*80)
        print("Enter mappings in format: original_name=standard_name")
        print("Separate multiple mappings with semicolons (;)")
        print("Press Enter without input to use suggested mappings")
        print("Example: CHR=chr;POS=pos;P_VALUE=pval")
        
        user_input = input("\nEnter mappings: ").strip()
        
        if not user_input and suggested_mapping:
            # Use suggested mappings
            return suggested_mapping
        elif user_input:
            # Parse batch input
            mapping = {}
            for pair in user_input.split(";"):
                if "=" in pair:
                    orig, std = pair.split("=", 1)
                    mapping[orig.strip()] = std.strip()
            return mapping
        else:
            return {}
    else:
        # Interactive mode - ask for each column
        mapping = {}
        
        print("\n" + "-"*80)
        print("INTERACTIVE MODE")
        print("-"*80)
        print("For each column, enter the standard name (or press Enter to skip)")
        
        for col in df.columns:
            suggested = suggested_mapping.get(col, "") if suggested_mapping else ""
            
            if suggested:
                prompt = f"\n{col} -> [{suggested}]: "
                user_input = input(prompt).strip()
                mapping[col] = user_input if user_input else suggested
            else:
                prompt = f"\n{col} -> "
                user_input = input(prompt).strip()
                if user_input:
                    mapping[col] = user_input
        
        return mapping


def preview_mapping(
    df: pd.DataFrame,
    mapping: Dict[str, str],
    n_rows: int = 5
) -> None:
    """
    Preview the column mapping result.
    
    Args:
        df: Original DataFrame
        mapping: Column mapping dictionary
        n_rows: Number of rows to preview
    """
    print("\n" + "="*80)
    print("MAPPING PREVIEW")
    print("="*80)
    
    print("\nColumn mapping:")
    for orig, std in mapping.items():
        print(f"  {orig} -> {std}")
    
    print(f"\nFirst {n_rows} rows of mapped data:")
    
    # Create preview with mapped columns
    preview_data = {}
    for orig, std in mapping.items():
        if orig in df.columns:
            preview_data[std] = df[orig].head(n_rows)
    
    preview_df = pd.DataFrame(preview_data)
    print(preview_df.to_string())
    
    # Show confirmation
    print("\n" + "-"*80)
    confirm = input("Accept this mapping? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("Mapping rejected. Please try again.")
        return False
    
    return True


def read_in_chunks(
    filename: str,
    chunksize: int = 100000,
    **read_kwargs
) -> pd.io.parsers.TextFileReader:
    """
    Read large files in chunks to handle gigabyte-sized data.
    
    Args:
        filename: Path to file
        chunksize: Number of rows per chunk
        **read_kwargs: Additional arguments for pd.read_csv
        
    Returns:
        TextFileReader iterator
    """
    return pd.read_csv(filename, chunksize=chunksize, **read_kwargs)


def process_large_file(
    filename: str,
    output_file: str,
    column_mapping: Dict[str, str],
    chunksize: int = 100000,
    verbose: bool = True,
    **read_kwargs
) -> None:
    """
    Process large files in chunks and write to output incrementally.
    
    Args:
        filename: Input file path
        output_file: Output file path
        column_mapping: Dictionary mapping original to standard column names
        chunksize: Number of rows per chunk
        verbose: Print progress information
        **read_kwargs: Additional arguments for reading file
    """
    if verbose:
        print(f"\nProcessing large file: {filename}")
        print(f"Chunk size: {chunksize} rows")
    
    chunk_iterator = read_in_chunks(filename, chunksize=chunksize, **read_kwargs)
    
    first_chunk = True
    total_rows = 0
    chunk_num = 0
    
    for chunk_df in chunk_iterator:
        chunk_num += 1
        
        # Apply column mapping
        mapped_chunk = pd.DataFrame()
        for orig_col, std_col in column_mapping.items():
            if orig_col in chunk_df.columns:
                mapped_chunk[std_col] = chunk_df[orig_col]
        
        # Write to output
        if first_chunk:
            mapped_chunk.to_csv(output_file, index=False, mode='w')
            first_chunk = False
        else:
            mapped_chunk.to_csv(output_file, index=False, mode='a', header=False)
        
        total_rows += len(chunk_df)
        
        if verbose and chunk_num % 10 == 0:
            print(f"  Processed {total_rows:,} rows...")
    
    if verbose:
        print(f"  Complete! Total rows processed: {total_rows:,}")
        print(f"  Output saved to: {output_file}")


def get_file_size_gb(filename: str) -> float:
    """Get file size in gigabytes."""
    size_bytes = Path(filename).stat().st_size
    return size_bytes / (1024 ** 3)


def suggest_chunk_size(filename: str, available_memory_gb: float = 4.0) -> int:
    """
    Suggest appropriate chunk size based on file size and available memory.
    
    Args:
        filename: Path to file
        available_memory_gb: Available memory in GB
        
    Returns:
        Suggested chunk size in rows
    """
    file_size_gb = get_file_size_gb(filename)
    
    if file_size_gb < 0.5:
        # Small file, no chunking needed
        return None
    elif file_size_gb < 2:
        # Medium file
        return 200000
    elif file_size_gb < 10:
        # Large file
        return 100000
    else:
        # Very large file
        return 50000


def create_omics_column_patterns() -> Dict[str, re.Pattern]:
    """
    Create comprehensive regex patterns for various omics data types.
    
    Returns:
        Dictionary of field names to regex patterns
    """
    patterns = {
        # Genomics
        "chr": re.compile(r"^(chr|chromosome|chrom|#?chr|#?chrom|#?CHROM|seqname)$", re.IGNORECASE),
        "pos": re.compile(r"^(pos|position|bp|base_pair|base_position|ps|POS|start|end)$", re.IGNORECASE),
        "ref": re.compile(r"^(ref|reference|ref_allele|reference_allele|REF|a2|allele2)$", re.IGNORECASE),
        "alt": re.compile(r"^(alt|alternate|alt_allele|alternate_allele|ALT|a1|allele1|effect_allele)$", re.IGNORECASE),
        "rsid": re.compile(r"^(rsid|snp|snpid|snp_id|variant_id|varid|id|ID|marker|rs)$", re.IGNORECASE),
        "pval": re.compile(r"^(p|pval|p_value|pvalue|p-value|p\.value|sig|pval_nominal|P)$", re.IGNORECASE),
        "beta": re.compile(r"^(beta|b|effect|coef|coefficient|effect_size|BETA|slope)$", re.IGNORECASE),
        "se": re.compile(r"^(se|stderr|standard_error|std_err|std_error|SE)$", re.IGNORECASE),
        "or": re.compile(r"^(or|odds_ratio|oddsratio|OR)$", re.IGNORECASE),
        "frq": re.compile(r"^(frq|freq|frequency|maf|af|eaf|allele_freq|AF)$", re.IGNORECASE),
        "n": re.compile(r"^(n|n_samples|sample_size|nsize|ns|n_total|ntotal|N)$", re.IGNORECASE),
        "info": re.compile(r"^(info|imputation_quality|impquality|r2|rsq|INFO)$", re.IGNORECASE),
        
        # Transcriptomics
        "gene_id": re.compile(r"^(gene_id|geneid|ensembl_id|ensembl|ensg)$", re.IGNORECASE),
        "gene_name": re.compile(r"^(gene_name|genename|gene_symbol|symbol|gene)$", re.IGNORECASE),
        "transcript_id": re.compile(r"^(transcript_id|transcriptid|enst)$", re.IGNORECASE),
        "expression": re.compile(r"^(expression|expr|value)$", re.IGNORECASE),
        "fpkm": re.compile(r"^(fpkm|rpkm)$", re.IGNORECASE),
        "tpm": re.compile(r"^(tpm|transcripts_per_million)$", re.IGNORECASE),
        "counts": re.compile(r"^(counts|read_count|reads)$", re.IGNORECASE),
        "log2fc": re.compile(r"^(log2fc|log2_fold_change|log2foldchange|lfc)$", re.IGNORECASE),
        "padj": re.compile(r"^(padj|adj_pval|adjusted_pvalue|fdr|qval|q_value)$", re.IGNORECASE),
        
        # Proteomics
        "protein_id": re.compile(r"^(protein_id|proteinid|uniprot|uniprot_id)$", re.IGNORECASE),
        "protein_name": re.compile(r"^(protein_name|proteinname|protein)$", re.IGNORECASE),
        "peptide": re.compile(r"^(peptide|peptide_sequence|sequence)$", re.IGNORECASE),
        "abundance": re.compile(r"^(abundance|protein_abundance)$", re.IGNORECASE),
        "intensity": re.compile(r"^(intensity|signal|signal_intensity)$", re.IGNORECASE),
        "ratio": re.compile(r"^(ratio|fold_change|fc)$", re.IGNORECASE),
        
        # Metabolomics
        "metabolite_id": re.compile(r"^(metabolite_id|metaboliteid|compound_id|hmdb|hmdb_id)$", re.IGNORECASE),
        "metabolite_name": re.compile(r"^(metabolite_name|metabolite|compound|compound_name)$", re.IGNORECASE),
        "mz": re.compile(r"^(mz|m/z|mass|mass_to_charge)$", re.IGNORECASE),
        "rt": re.compile(r"^(rt|retention_time|retentiontime)$", re.IGNORECASE),
        "concentration": re.compile(r"^(concentration|conc|amount)$", re.IGNORECASE),
        "peak_area": re.compile(r"^(peak_area|area|peak_intensity)$", re.IGNORECASE),
        
        # Sample information
        "sample_id": re.compile(r"^(sample_id|sampleid|sample|sample_name)$", re.IGNORECASE),
        "condition": re.compile(r"^(condition|group|treatment|class)$", re.IGNORECASE),
        "timepoint": re.compile(r"^(timepoint|time|time_point)$", re.IGNORECASE),
        "replicate": re.compile(r"^(replicate|rep|biological_replicate)$", re.IGNORECASE),
        "batch": re.compile(r"^(batch|batch_id)$", re.IGNORECASE),
    }
    
    return patterns


def auto_detect_omics_type(df: pd.DataFrame) -> str:
    """
    Automatically detect the type of omics data based on column names.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Detected omics type (genomics, transcriptomics, proteomics, metabolomics, unknown)
    """
    columns_lower = [col.lower() for col in df.columns]
    
    # Score for each omics type
    scores = {
        'genomics': 0,
        'transcriptomics': 0,
        'proteomics': 0,
        'metabolomics': 0
    }
    
    # Genomics indicators
    genomics_keywords = ['chr', 'chrom', 'chromosome', 'pos', 'position', 'snp', 'rsid', 'ref', 'alt', 'vcf']
    for kw in genomics_keywords:
        if any(kw in col for col in columns_lower):
            scores['genomics'] += 1
    
    # Transcriptomics indicators
    transcriptomics_keywords = ['gene', 'transcript', 'fpkm', 'tpm', 'counts', 'expression', 'ensg', 'enst']
    for kw in transcriptomics_keywords:
        if any(kw in col for col in columns_lower):
            scores['transcriptomics'] += 1
    
    # Proteomics indicators
    proteomics_keywords = ['protein', 'peptide', 'uniprot', 'abundance', 'intensity']
    for kw in proteomics_keywords:
        if any(kw in col for col in columns_lower):
            scores['proteomics'] += 1
    
    # Metabolomics indicators
    metabolomics_keywords = ['metabolite', 'compound', 'hmdb', 'mz', 'm/z', 'retention', 'peak']
    for kw in metabolomics_keywords:
        if any(kw in col for col in columns_lower):
            scores['metabolomics'] += 1
    
    # Return the type with highest score
    max_score = max(scores.values())
    if max_score == 0:
        return 'unknown'
    
    return max(scores, key=scores.get)


def match_column(column_name: str, patterns: Dict[str, re.Pattern]) -> Optional[str]:
    """
    Match a single column name to standardized field using regex patterns.
    
    Args:
        column_name: Column name to match
        patterns: Dictionary of regex patterns
        
    Returns:
        Matched standard field name or None
    """
    for field, pattern in patterns.items():
        if pattern.match(column_name.strip()):
            return field
    return None


def auto_suggest_mapping(
    df: pd.DataFrame,
    custom_patterns: Optional[Dict[str, re.Pattern]] = None
) -> Dict[str, str]:
    """
    Automatically suggest column mappings based on patterns.
    
    Args:
        df: DataFrame to analyze
        custom_patterns: Optional custom regex patterns
        
    Returns:
        Dictionary of suggested mappings
    """
    patterns = create_omics_column_patterns()
    
    if custom_patterns:
        patterns.update(custom_patterns)
    
    suggested = {}
    for col in df.columns:
        matched = match_column(col, patterns)
        if matched:
            suggested[col] = matched
    
    return suggested
