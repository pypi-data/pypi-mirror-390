"""
Conversion Report Module
Generates detailed reports of data conversion operations
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json


class ConversionReport:
    """
    Tracks and generates reports for data conversion operations.
    """
    
    def __init__(self):
        self.input_file = None
        self.output_file = None
        self.conversion_time = None
        self.original_columns = []
        self.final_columns = []
        self.column_mapping = {}
        self.unmapped_columns = []
        self.rows_processed = 0
        self.omics_type = "unknown"
        self.file_size_mb = 0
        self.processing_method = "in-memory"
        self.chunk_size = None
        
    def set_input_info(self, filename: str, columns: List[str], rows: int, 
                       file_size_mb: float, omics_type: str = "unknown"):
        """Set input file information."""
        self.input_file = filename
        self.original_columns = columns
        self.rows_processed = rows
        self.file_size_mb = file_size_mb
        self.omics_type = omics_type
        
    def set_output_info(self, filename: str, columns: List[str]):
        """Set output file information."""
        self.output_file = filename
        self.final_columns = columns
        
    def set_column_mapping(self, mapping: Dict[str, str], unmapped: List[str] = None):
        """Set column mapping information."""
        self.column_mapping = mapping
        self.unmapped_columns = unmapped or []
        
    def set_processing_info(self, method: str = "in-memory", chunk_size: int = None):
        """Set processing method information."""
        self.processing_method = method
        self.chunk_size = chunk_size
        self.conversion_time = datetime.now()
        
    def generate_text_report(self) -> str:
        """
        Generate a human-readable text report.
        
        Returns:
            Formatted text report as string
        """
        report_lines = [
            "="*80,
            "BIOINFORMATICS DATA CONVERSION REPORT",
            "="*80,
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "INPUT INFORMATION",
            "-"*80,
            f"File: {self.input_file}",
            f"File Size: {self.file_size_mb:.2f} MB",
            f"Detected Type: {self.omics_type}",
            f"Rows: {self.rows_processed:,}",
            f"Original Columns: {len(self.original_columns)}",
            "",
            "PROCESSING INFORMATION",
            "-"*80,
            f"Method: {self.processing_method}",
        ]
        
        if self.chunk_size:
            report_lines.append(f"Chunk Size: {self.chunk_size:,} rows")
        
        report_lines.extend([
            "",
            "COLUMN MAPPING",
            "-"*80,
            f"Columns Mapped: {len(self.column_mapping)}",
            f"Columns Unmapped: {len(self.unmapped_columns)}",
            "",
        ])
        
        if self.column_mapping:
            report_lines.append("Mapped Columns:")
            for original, standard in sorted(self.column_mapping.items()):
                report_lines.append(f"  {original:30s} -> {standard}")
            report_lines.append("")
        
        if self.unmapped_columns:
            report_lines.append("Unmapped Columns:")
            for col in sorted(self.unmapped_columns):
                report_lines.append(f"  - {col}")
            report_lines.append("")
        
        report_lines.extend([
            "OUTPUT INFORMATION",
            "-"*80,
            f"File: {self.output_file}",
            f"Final Columns: {len(self.final_columns)}",
            f"Rows Written: {self.rows_processed:,}",
            "",
        ])
        
        # Column summary
        report_lines.extend([
            "COLUMN SUMMARY",
            "-"*80,
            "Original Columns:",
        ])
        for col in self.original_columns:
            status = "mapped" if col in self.column_mapping else "unmapped"
            target = f" -> {self.column_mapping[col]}" if col in self.column_mapping else ""
            report_lines.append(f"  [{status:8s}] {col}{target}")
        
        report_lines.extend([
            "",
            "="*80,
            "END OF REPORT",
            "="*80,
        ])
        
        return "\n".join(report_lines)
    
    def generate_json_report(self) -> str:
        """
        Generate a machine-readable JSON report.
        
        Returns:
            JSON string with conversion details
        """
        report_data = {
            "conversion_time": self.conversion_time.isoformat() if self.conversion_time else None,
            "input": {
                "file": self.input_file,
                "file_size_mb": self.file_size_mb,
                "omics_type": self.omics_type,
                "rows": self.rows_processed,
                "columns": self.original_columns,
                "column_count": len(self.original_columns)
            },
            "processing": {
                "method": self.processing_method,
                "chunk_size": self.chunk_size
            },
            "mapping": {
                "mapped_columns": self.column_mapping,
                "unmapped_columns": self.unmapped_columns,
                "mapping_count": len(self.column_mapping),
                "unmapped_count": len(self.unmapped_columns)
            },
            "output": {
                "file": self.output_file,
                "columns": self.final_columns,
                "column_count": len(self.final_columns),
                "rows": self.rows_processed
            }
        }
        
        return json.dumps(report_data, indent=2)
    
    def generate_csv_mapping(self) -> pd.DataFrame:
        """
        Generate a CSV-friendly DataFrame of column mappings.
        
        Returns:
            DataFrame with mapping details
        """
        mapping_data = []
        
        # Add mapped columns
        for original, standard in self.column_mapping.items():
            mapping_data.append({
                "original_column": original,
                "standard_column": standard,
                "status": "mapped",
                "included_in_output": "yes"
            })
        
        # Add unmapped columns
        for col in self.unmapped_columns:
            mapping_data.append({
                "original_column": col,
                "standard_column": "",
                "status": "unmapped",
                "included_in_output": "no"
            })
        
        return pd.DataFrame(mapping_data)
    
    def save_report(self, output_dir: str, base_name: str = "conversion_report"):
        """
        Save conversion report in multiple formats.
        
        Args:
            output_dir: Directory to save reports
            base_name: Base name for report files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save text report
        text_file = output_path / f"{base_name}.txt"
        with open(text_file, 'w') as f:
            f.write(self.generate_text_report())
        print(f"Text report saved: {text_file}")
        
        # Save JSON report
        json_file = output_path / f"{base_name}.json"
        with open(json_file, 'w') as f:
            f.write(self.generate_json_report())
        print(f"JSON report saved: {json_file}")
        
        # Save mapping CSV
        csv_file = output_path / f"{base_name}_mapping.csv"
        self.generate_csv_mapping().to_csv(csv_file, index=False)
        print(f"Mapping CSV saved: {csv_file}")
    
    def print_summary(self):
        """Print a brief summary of the conversion."""
        print("\n" + "="*80)
        print("CONVERSION SUMMARY")
        print("="*80)
        print(f"Input:  {self.input_file}")
        print(f"Output: {self.output_file}")
        print(f"Omics Type: {self.omics_type}")
        print(f"Rows: {self.rows_processed:,}")
        print(f"Columns: {len(self.original_columns)} -> {len(self.final_columns)}")
        print(f"Mapped: {len(self.column_mapping)}, Unmapped: {len(self.unmapped_columns)}")
        print("="*80)
