#' Universal Bioinformatics Data Converter
#'
#' @description
#' R interface to the bioconverter Python package for converting various
#' bioinformatics data formats to unified standard formats.
#'
#' @docType package
#' @name bioconverter
NULL

# Module-level variable to store Python module
.convertor <- NULL
.interactive_converter <- NULL
.conversion_report <- NULL

#' Initialize bioconverter Python modules
#'
#' @description
#' Load the Python modules required for bioconverter.
#' This is called automatically when needed.
#'
#' @return NULL (called for side effects)
#' @keywords internal
.init_python_modules <- function() {
  if (is.null(.convertor)) {
    # Check if reticulate is available
    if (!requireNamespace("reticulate", quietly = TRUE)) {
      stop("Package 'reticulate' is required but not installed.")
    }
    
    # Import Python modules
    .convertor <<- reticulate::import("convertor", delay_load = TRUE)
    .interactive_converter <<- reticulate::import("interactive_converter", delay_load = TRUE)
    .conversion_report <<- reticulate::import("conversion_report", delay_load = TRUE)
  }
}

#' Convert a bioinformatics data file
#'
#' @description
#' Convert a bioinformatics data file from its original format to a standardized format.
#' Automatically detects file format and omics type.
#'
#' @param input_file Character. Path to input file
#' @param output_file Character. Path to output file
#' @param auto_suggest Logical. Use automatic column mapping suggestions (default: TRUE)
#' @param column_mapping Named list. Manual column mapping (original_name = "standard_name")
#' @param keep_unmatched Logical. Keep columns that don't match standard patterns (default: FALSE)
#' @param verbose Logical. Print detailed information (default: TRUE)
#' @param generate_report Logical. Generate conversion report (default: TRUE)
#' @param report_dir Character. Directory for saving reports (default: same as output)
#'
#' @return A tibble containing the converted data
#'
#' @examples
#' \dontrun{
#' # Convert with auto-suggestion
#' result <- convert_file(
#'   input_file = "gwas_data.tsv",
#'   output_file = "standardized_gwas.tsv"
#' )
#'
#' # Convert with manual mapping
#' result <- convert_file(
#'   input_file = "data.txt",
#'   output_file = "output.tsv",
#'   column_mapping = list(CHR = "chr", POS = "pos", P = "pval")
#' )
#' }
#'
#' @export
convert_file <- function(input_file,
                        output_file,
                        auto_suggest = TRUE,
                        column_mapping = NULL,
                        keep_unmatched = FALSE,
                        verbose = TRUE,
                        generate_report = TRUE,
                        report_dir = NULL) {
  .init_python_modules()
  
  # Convert R list to Python dict if provided
  py_mapping <- if (!is.null(column_mapping)) {
    reticulate::dict(column_mapping)
  } else {
    NULL
  }
  
  # Call Python conversion function
  result_df <- .convertor$convert_single_file(
    filename = input_file,
    column_mapping = py_mapping,
    keep_unmatched = keep_unmatched,
    verbose = verbose
  )
  
  # Save output
  if (verbose) {
    cat(sprintf("\nSaving output to: %s\n", output_file))
  }
  
  # Convert pandas DataFrame to R tibble
  r_df <- tibble::as_tibble(result_df)
  
  # Write output file
  readr::write_tsv(r_df, output_file)
  
  # Generate report if requested
  if (generate_report) {
    if (is.null(report_dir)) {
      report_dir <- dirname(output_file)
    }
    
    report <- generate_conversion_report(
      input_file = input_file,
      output_file = output_file,
      original_columns = colnames(readr::read_tsv(input_file, n_max = 1, show_col_types = FALSE)),
      final_columns = colnames(r_df),
      column_mapping = if (!is.null(column_mapping)) column_mapping else list(),
      report_dir = report_dir
    )
    
    if (verbose) {
      cat("\nConversion report generated in:", report_dir, "\n")
    }
  }
  
  return(r_df)
}

#' Get supported column name patterns
#'
#' @description
#' Retrieve all supported column name patterns for automatic mapping.
#'
#' @return A list of pattern categories and their recognized variations
#'
#' @examples
#' \dontrun{
#' patterns <- get_column_patterns()
#' print(patterns$genomics)
#' }
#'
#' @export
get_column_patterns <- function() {
  .init_python_modules()
  
  patterns <- .interactive_converter$create_omics_column_patterns()
  
  # Convert to R list with readable format
  pattern_list <- list(
    genomics = c("chr", "pos", "rsid", "ref", "alt", "pval", "beta", "se", "or", "frq", "n", "info"),
    transcriptomics = c("gene_id", "gene_name", "transcript_id", "expression", "fpkm", "tpm", "counts", "log2fc", "padj"),
    proteomics = c("protein_id", "protein_name", "peptide", "abundance", "intensity", "ratio"),
    metabolomics = c("metabolite_id", "metabolite_name", "mz", "rt", "concentration", "peak_area"),
    sample_info = c("sample_id", "condition", "timepoint", "replicate", "batch")
  )
  
  return(pattern_list)
}

#' Auto-suggest column mappings
#'
#' @description
#' Automatically suggest column mappings based on recognized patterns.
#'
#' @param input_file Character. Path to input file
#' @param n_rows Integer. Number of rows to read for analysis (default: 1000)
#'
#' @return A named list with suggested column mappings
#'
#' @examples
#' \dontrun{
#' suggestions <- auto_suggest_mapping("gwas_data.tsv")
#' print(suggestions)
#' }
#'
#' @export
auto_suggest_mapping <- function(input_file, n_rows = 1000) {
  .init_python_modules()
  
  # Read sample data
  sample_df <- readr::read_tsv(input_file, n_max = n_rows, show_col_types = FALSE)
  
  # Convert to pandas DataFrame
  py_df <- reticulate::r_to_py(sample_df)
  
  # Get suggestions
  suggestions <- .interactive_converter$auto_suggest_mapping(py_df)
  
  # Convert to R list
  return(as.list(suggestions))
}

#' Generate conversion report
#'
#' @description
#' Generate a detailed report of the data conversion process.
#'
#' @param input_file Character. Path to input file
#' @param output_file Character. Path to output file
#' @param original_columns Character vector. Original column names
#' @param final_columns Character vector. Final column names
#' @param column_mapping Named list. Column mapping used
#' @param report_dir Character. Directory to save reports
#' @param omics_type Character. Detected omics type (optional)
#'
#' @return Path to generated report files
#'
#' @export
generate_conversion_report <- function(input_file,
                                      output_file,
                                      original_columns,
                                      final_columns,
                                      column_mapping,
                                      report_dir,
                                      omics_type = "unknown") {
  .init_python_modules()
  
  # Create report object
  report <- .conversion_report$ConversionReport()
  
  # Set information
  file_size_mb <- file.info(input_file)$size / (1024^2)
  report$set_input_info(
    filename = input_file,
    columns = original_columns,
    rows = length(readr::read_lines(input_file)) - 1,  # Approximate
    file_size_mb = file_size_mb,
    omics_type = omics_type
  )
  
  report$set_output_info(
    filename = output_file,
    columns = final_columns
  )
  
  # Get mapped and unmapped columns
  unmapped <- setdiff(original_columns, names(column_mapping))
  report$set_column_mapping(
    mapping = reticulate::dict(column_mapping),
    unmapped = unmapped
  )
  
  report$set_processing_info()
  
  # Save reports
  report$save_report(report_dir, "conversion_report")
  
  return(file.path(report_dir, "conversion_report"))
}

#' Convert with interactive column mapping (wrapper for Python CLI)
#'
#' @description
#' This function provides information about using the Python CLI for
#' interactive conversion. R doesn't support interactive stdin well,
#' so use the Python CLI directly.
#'
#' @param input_file Character. Path to input file
#'
#' @return Information message about using Python CLI
#'
#' @examples
#' \dontrun{
#' convert_with_mapping("data.tsv")
#' }
#'
#' @export
convert_with_mapping <- function(input_file) {
  cat("\nInteractive column mapping is best done through the Python CLI.\n")
  cat("Please run the following command in your terminal:\n\n")
  cat(sprintf("  python3 cli.py -i %s -o output.tsv --interactive\n\n", input_file))
  cat("Alternatively, use auto_suggest_mapping() to get suggestions,\n")
  cat("then use convert_file() with the column_mapping parameter.\n")
}
