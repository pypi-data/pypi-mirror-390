#!/usr/bin/env python3
"""
Command-line interface for the Bioinformatics Data Converter
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
from convertor import (
    convert_single_file,
    detect_file_format,
    standardize_columns,
    read_data,
)
from interactive_converter import (
    interactive_column_mapping,
    preview_mapping,
    process_large_file,
    get_file_size_gb,
    suggest_chunk_size,
    auto_suggest_mapping,
    auto_detect_omics_type,
    create_omics_column_patterns,
)
from conversion_report import ConversionReport


def main():
    parser = argparse.ArgumentParser(
        description="Bioinformatics Data Converter - Convert various omics data formats to unified format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode with auto-detection
  %(prog)s -i input.tsv -o output.tsv --interactive
  
  # Batch mode with suggested mappings
  %(prog)s -i input.csv -o output.csv --auto-suggest
  
  # Process large file with chunking
  %(prog)s -i large_file.txt -o output.tsv --chunk-size 100000
  
  # Manual column mapping
  %(prog)s -i input.txt -o output.tsv --map "CHR=chr,POS=pos,P_VALUE=pval"
  
  # Detect file information only
  %(prog)s -i input.vcf.gz --info-only

Supported data types:
  - Genomics: VCF, GWAS summary statistics, SNP data
  - Transcriptomics: RNA-seq counts, FPKM/TPM, differential expression
  - Proteomics: Protein abundance, peptide intensity
  - Metabolomics: Metabolite concentrations, peak areas
        """
    )
    
    # Input/Output arguments
    parser.add_argument(
        "-i", "--input",
        help="Input file path"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (required unless --info-only is specified)"
    )
    
    # File format arguments
    parser.add_argument(
        "--sep",
        help="Column separator (auto-detected if not specified)"
    )
    parser.add_argument(
        "--compression",
        choices=['gzip', 'bz2', 'zip', 'xz'],
        help="Compression format (auto-detected if not specified)"
    )
    parser.add_argument(
        "--comment",
        help="Comment character for lines to skip"
    )
    parser.add_argument(
        "--vcf",
        action='store_true',
        help="Treat as VCF format"
    )
    
    # Column mapping modes
    mapping_group = parser.add_mutually_exclusive_group()
    mapping_group.add_argument(
        "--interactive",
        action='store_true',
        help="Interactive column mapping mode"
    )
    mapping_group.add_argument(
        "--batch-interactive",
        action='store_true',
        help="Batch interactive mode (enter all mappings at once)"
    )
    mapping_group.add_argument(
        "--auto-suggest",
        action='store_true',
        help="Use auto-suggested mappings without interaction"
    )
    mapping_group.add_argument(
        "--map",
        help='Manual mapping as comma-separated pairs: "old1=new1,old2=new2"'
    )
    
    # Large file handling
    parser.add_argument(
        "--chunk-size",
        type=int,
        help="Chunk size for processing large files (auto-suggested if not specified)"
    )
    parser.add_argument(
        "--memory",
        type=float,
        default=4.0,
        help="Available memory in GB for chunk size estimation (default: 4.0)"
    )
    
    # Output options
    parser.add_argument(
        "--keep-unmatched",
        action='store_true',
        help="Keep columns that don't match any standard pattern"
    )
    parser.add_argument(
        "--output-format",
        choices=['csv', 'tsv', 'parquet'],
        default='tsv',
        help="Output format (default: tsv)"
    )
    parser.add_argument(
        "--no-compression",
        action='store_true',
        help="Don't compress output file"
    )
    
    # Information and debugging
    parser.add_argument(
        "--info-only",
        action='store_true',
        help="Only show file information without conversion"
    )
    parser.add_argument(
        "--preview",
        type=int,
        default=5,
        help="Number of rows to preview (default: 5)"
    )
    parser.add_argument(
        "--verbose",
        action='store_true',
        help="Verbose output"
    )
    parser.add_argument(
        "--show-patterns",
        action='store_true',
        help="Show all supported column name patterns and exit"
    )
    
    # Report generation
    parser.add_argument(
        "--generate-report",
        action='store_true',
        default=True,
        help="Generate conversion report (default: True)"
    )
    parser.add_argument(
        "--no-report",
        dest='generate_report',
        action='store_false',
        help="Don't generate conversion report"
    )
    parser.add_argument(
        "--report-dir",
        help="Directory for conversion reports (default: same as output)"
    )
    
    args = parser.parse_args()
    
    # Show patterns and exit if requested
    if args.show_patterns:
        show_patterns()
        return 0
    
    # Validate input argument
    if not args.input:
        parser.error("-i/--input is required unless --show-patterns is specified")
    
    # Validate output argument
    if not args.info_only and not args.output:
        parser.error("--output is required unless --info-only is specified")
    
    # Get input file info
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1
    
    # Auto-detect file format
    sep, compression, comment, is_vcf = detect_file_format(args.input)
    
    # Override with user-specified values
    if args.sep:
        sep = args.sep
    if args.compression:
        compression = args.compression
    if args.comment:
        comment = args.comment
    if args.vcf:
        is_vcf = True
    
    # Get file size
    file_size_gb = get_file_size_gb(args.input)
    
    # Print file information
    print("="*80)
    print("FILE INFORMATION")
    print("="*80)
    print(f"Input file: {args.input}")
    print(f"File size: {file_size_gb:.2f} GB")
    print(f"Separator: {repr(sep)}")
    print(f"Compression: {compression}")
    print(f"VCF format: {is_vcf}")
    
    # Read first chunk to analyze
    print("\nReading sample data for analysis...")
    try:
        if is_vcf:
            from convertor import read_vcf_file
            sample_df = read_vcf_file(args.input, compression=compression)
            if len(sample_df) > 1000:
                sample_df = sample_df.head(1000)
        else:
            sample_df = pd.read_csv(
                args.input,
                sep=sep,
                compression=compression,
                comment=comment,
                nrows=1000
            )
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1
    
    print(f"Columns found: {len(sample_df.columns)}")
    print(f"Sample rows: {len(sample_df)}")
    
    # Detect omics type
    omics_type = auto_detect_omics_type(sample_df)
    print(f"Detected data type: {omics_type}")
    
    # Show column preview
    print("\nColumns:")
    for i, col in enumerate(sample_df.columns, 1):
        print(f"  {i}. {col}")
    
    # If info-only mode, exit here
    if args.info_only:
        print("\nData preview:")
        print(sample_df.head(args.preview).to_string())
        return 0
    
    # Auto-suggest column mappings
    suggested_mapping = auto_suggest_mapping(sample_df)
    
    if suggested_mapping and args.verbose:
        print("\nAuto-suggested mappings:")
        for orig, std in suggested_mapping.items():
            print(f"  {orig} -> {std}")
    
    # Determine column mapping based on mode
    column_mapping = None
    
    if args.map:
        # Manual mapping
        column_mapping = {}
        for pair in args.map.split(','):
            if '=' in pair:
                old, new = pair.split('=', 1)
                column_mapping[old.strip()] = new.strip()
        print("\nUsing manual column mapping")
        
    elif args.interactive or args.batch_interactive:
        # Interactive mapping
        column_mapping = interactive_column_mapping(
            sample_df,
            suggested_mapping=suggested_mapping,
            batch_mode=args.batch_interactive
        )
        
        # Preview and confirm
        if column_mapping:
            accepted = preview_mapping(sample_df, column_mapping, n_rows=args.preview)
            if not accepted:
                print("Conversion cancelled by user")
                return 1
        else:
            print("No column mappings provided")
            return 1
            
    elif args.auto_suggest:
        # Use auto-suggested mappings
        column_mapping = suggested_mapping
        if not column_mapping:
            print("Warning: No columns could be auto-mapped", file=sys.stderr)
            if not args.keep_unmatched:
                print("Consider using --interactive mode or --keep-unmatched flag")
                return 1
        print("\nUsing auto-suggested mappings")
    else:
        # No mapping specified, try auto-suggest
        if suggested_mapping:
            print("\nNo mapping mode specified. Using auto-suggested mappings.")
            print("Use --interactive for manual control or --map for explicit mapping.")
            column_mapping = suggested_mapping
        else:
            print("Error: No mapping mode specified and no columns could be auto-mapped", file=sys.stderr)
            print("Use --interactive, --batch-interactive, --auto-suggest, or --map")
            return 1
    
    # Determine if we need chunked processing
    chunk_size = args.chunk_size
    if chunk_size is None and file_size_gb > 0.5:
        chunk_size = suggest_chunk_size(args.input, args.memory)
        if chunk_size and args.verbose:
            print(f"\nUsing chunked processing with chunk size: {chunk_size:,} rows")
    
    # Process file
    print("\n" + "="*80)
    print("PROCESSING")
    print("="*80)
    
    try:
        if chunk_size:
            # Large file processing
            output_path = args.output
            
            # Determine read kwargs
            read_kwargs = {
                'sep': sep,
                'compression': compression,
            }
            if comment:
                read_kwargs['comment'] = comment
            
            process_large_file(
                args.input,
                output_path,
                column_mapping,
                chunksize=chunk_size,
                verbose=args.verbose,
                **read_kwargs
            )
        else:
            # Regular processing
            df = read_data(
                args.input,
                sep=sep,
                compression=compression,
                comment=comment,
                is_vcf=is_vcf
            )
            
            if args.verbose:
                print(f"Loaded data: {df.shape[0]:,} rows, {df.shape[1]} columns")
            
            # Apply mapping
            result_df = pd.DataFrame()
            for orig_col, std_col in column_mapping.items():
                if orig_col in df.columns:
                    result_df[std_col] = df[orig_col]
            
            # Keep unmatched columns if requested
            if args.keep_unmatched:
                for col in df.columns:
                    if col not in column_mapping and col not in result_df.columns:
                        result_df[col] = df[col]
            
            if args.verbose:
                print(f"Converted data: {result_df.shape[0]:,} rows, {result_df.shape[1]} columns")
            
            # Save output
            output_compression = None if args.no_compression else 'gzip'
            
            if args.output_format == 'parquet':
                result_df.to_parquet(args.output, compression=output_compression or 'snappy')
            elif args.output_format == 'csv':
                result_df.to_csv(args.output, index=False, compression=output_compression)
            else:  # tsv
                result_df.to_csv(args.output, sep='\t', index=False, compression=output_compression)
            
            print(f"\nOutput saved to: {args.output}")
        
        # Generate conversion report
        if args.generate_report:
            report_dir = args.report_dir or Path(args.output).parent
            
            # Create report
            report = ConversionReport()
            report.set_input_info(
                filename=args.input,
                columns=sample_df.columns.tolist(),
                rows=len(df) if not chunk_size else None,
                file_size_mb=file_size_gb * 1024,
                omics_type=omics_type
            )
            
            report.set_output_info(
                filename=args.output,
                columns=list(column_mapping.values()) if not args.keep_unmatched else result_df.columns.tolist() if not chunk_size else list(column_mapping.values())
            )
            
            # Get unmapped columns
            unmapped = [col for col in sample_df.columns if col not in column_mapping]
            report.set_column_mapping(column_mapping, unmapped)
            
            # Set processing info
            if chunk_size:
                report.set_processing_info(method="chunked", chunk_size=chunk_size)
            else:
                report.set_processing_info(method="in-memory")
            
            # Save reports
            report.save_report(str(report_dir), "conversion_report")
            report.print_summary()
        
        print("\n" + "="*80)
        print("CONVERSION COMPLETE")
        print("="*80)
        
        return 0
        
    except Exception as e:
        print(f"\nError during conversion: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def show_patterns():
    """Display all supported column name patterns."""
    print("="*80)
    print("SUPPORTED COLUMN NAME PATTERNS")
    print("="*80)
    
    patterns = create_omics_column_patterns()
    
    # Group by category
    categories = {
        'Genomics': ['chr', 'pos', 'ref', 'alt', 'rsid', 'pval', 'beta', 'se', 'or', 'frq', 'n', 'info'],
        'Transcriptomics': ['gene_id', 'gene_name', 'transcript_id', 'expression', 'fpkm', 'tpm', 'counts', 'log2fc', 'padj'],
        'Proteomics': ['protein_id', 'protein_name', 'peptide', 'abundance', 'intensity', 'ratio'],
        'Metabolomics': ['metabolite_id', 'metabolite_name', 'mz', 'rt', 'concentration', 'peak_area'],
        'Sample Info': ['sample_id', 'condition', 'timepoint', 'replicate', 'batch'],
    }
    
    for category, fields in categories.items():
        print(f"\n{category}:")
        print("-" * 40)
        for field in fields:
            if field in patterns:
                pattern = patterns[field]
                pattern_str = pattern.pattern
                # Clean up regex for display
                pattern_str = pattern_str.replace('^', '').replace('$', '').replace('(', '').replace(')', '')
                options = [opt for opt in pattern_str.split('|') if opt]
                print(f"  {field:20s} <- {', '.join(options[:5])}")
                if len(options) > 5:
                    print(f"  {' '*20}    (and {len(options)-5} more...)")


if __name__ == "__main__":
    sys.exit(main())
