import pandas as pd
import re
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import gzip


def read_vcf_file(fn: str, compression: Optional[str] = None) -> pd.DataFrame:
    """
    专门读取VCF文件，处理##注释和#CHROM列名

    Args:
        fn: 文件路径
        compression: 压缩格式

    Returns:
        DataFrame
    """
    # 确定打开方式
    if compression == "gzip" or fn.endswith(".gz"):
        opener = gzip.open
        mode = "rt"
    else:
        opener = open
        mode = "r"

    # 第一遍：找到列名和数据开始位置
    header_line = None
    data_start_line = 0

    with opener(fn, mode) as f:
        for i, line in enumerate(f):
            if line.startswith("#CHROM"):
                # 找到列名行
                header_line = line.strip()
                data_start_line = i + 1
                break
            elif line.startswith("CHROM") and not line.startswith("##"):
                # 没有#的列名行
                header_line = line.strip()
                data_start_line = i + 1
                break

    if header_line is None:
        raise ValueError(f"Could not find header line in VCF file: {fn}")

    # 解析列名
    columns = header_line.split("\t")
    columns = [col.lstrip("#") for col in columns]  # 移除开头的#

    # 第二遍：读取数据（跳过所有注释行）
    data_rows = []
    with opener(fn, mode) as f:
        for i, line in enumerate(f):
            if i < data_start_line:
                continue
            if line.startswith("#"):
                continue
            data_rows.append(line.strip().split("\t"))

    # 创建DataFrame
    df = pd.DataFrame(data_rows, columns=columns)

    return df


def read_data(
    fn: str,
    sep: str = r"\s+",
    compression: Optional[str] = None,
    comment: Optional[str] = None,
    is_vcf: bool = False,
) -> pd.DataFrame:
    """
    读取遗传学数据文件

    Args:
        fn: 文件路径
        sep: 分隔符，默认空白符
        compression: 压缩格式 (None, 'gzip', 'bz2', 'zip', 'xz')
        comment: 注释符号，以此开头的行将被忽略
        is_vcf: 是否是VCF文件

    Returns:
        DataFrame
    """
    if is_vcf:
        return read_vcf_file(fn, compression)
    else:
        return pd.read_csv(fn, sep=sep, compression=compression, comment=comment)


def create_genetic_column_patterns() -> Dict[str, re.Pattern]:
    """
    创建用于匹配遗传学数据常见列名的正则表达式模式

    Returns:
        字典，键为标准字段名，值为对应的正则表达式模式
    """
    patterns = {
        # Genomics
        "chr": re.compile(
            r"^(chr|chromosome|chrom|#?chr|#?chrom|#?CHROM|seqname)$", re.IGNORECASE
        ),
        "pos": re.compile(
            r"^(pos|position|bp|base_pair|base_position|ps|POS|start|end)$", re.IGNORECASE
        ),
        "a1": re.compile(
            r"^(a1|allele1|allele_1|effect_allele|ea|alt|alt_allele|ALT)$",
            re.IGNORECASE,
        ),
        "a2": re.compile(
            r"^(a2|allele2|allele_2|other_allele|oa|ref|ref_allele|reference_allele|REF)$",
            re.IGNORECASE,
        ),
        "n": re.compile(
            r"^(n|n_samples|sample_size|nsize|ns|n_total|ntotal|N)$", re.IGNORECASE
        ),
        "frq": re.compile(
            r"^(frq|freq|frequency|maf|af|eaf|allele_freq|allele_frequency|a1_freq|effect_allele_freq|AF)$",
            re.IGNORECASE,
        ),
        "info": re.compile(
            r"^(info|imputation_quality|impquality|r2|rsq|INFO)$", re.IGNORECASE
        ),
        "beta": re.compile(
            r"^(beta|b|effect|coef|coefficient|effect_size|BETA|slope)$", re.IGNORECASE
        ),
        "or": re.compile(r"^(or|odds_ratio|oddsratio|OR)$", re.IGNORECASE),
        "z": re.compile(r"^(z|zscore|z_score|zstat|z_statistic)$", re.IGNORECASE),
        "rsid": re.compile(
            r"^(rsid|snp|snpid|snp_id|variant_id|varid|id|marker|markername|rs|ID)$",
            re.IGNORECASE,
        ),
        "pval": re.compile(
            r"^(p|pval|p_value|pvalue|p-value|p.value|sig|pval_nominal|P)$", re.IGNORECASE
        ),
        "se": re.compile(
            r"^(se|stderr|standard_error|std_err|std_error|SE)$", re.IGNORECASE
        ),
        
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


def match_column(column_name: str, patterns: Dict[str, re.Pattern]) -> Optional[str]:
    """
    匹配单个列名到标准化字段

    Args:
        column_name: 待匹配的列名
        patterns: 正则表达式模式字典

    Returns:
        匹配到的标准字段名，如果没有匹配返回None
    """
    for field, pattern in patterns.items():
        if pattern.match(column_name.strip()):
            return field
    return None


def match_columns(
    column_list: List[str], custom_patterns: Optional[Dict[str, re.Pattern]] = None
) -> Dict[str, Optional[str]]:
    """
    批量匹配列名列表

    Args:
        column_list: 列名列表
        custom_patterns: 自定义的正则表达式模式字典，会覆盖默认模式

    Returns:
        字典，键为原始列名，值为匹配到的标准字段名
    """
    patterns = create_genetic_column_patterns()

    # 如果提供了自定义模式，更新默认模式
    if custom_patterns:
        patterns.update(custom_patterns)

    result = {}
    for col in column_list:
        matched = match_column(col, patterns)
        result[col] = matched

    return result


def detect_file_format(filename: str) -> Tuple[str, Optional[str], Optional[str], bool]:
    """
    根据文件扩展名自动检测分隔符、压缩格式、注释符和是否为VCF

    Args:
        filename: 文件路径

    Returns:
        (分隔符, 压缩格式, 注释符, 是否VCF) 元组
    """
    path = Path(filename)
    suffixes = "".join(path.suffixes).lower()

    # 检测压缩格式
    compression = None
    if ".gz" in suffixes:
        compression = "gzip"
    elif ".bz2" in suffixes:
        compression = "bz2"
    elif ".zip" in suffixes:
        compression = "zip"
    elif ".xz" in suffixes:
        compression = "xz"

    # 检测分隔符、注释符和是否为VCF
    comment = None
    is_vcf = False
    if ".vcf" in suffixes:
        sep = "\t"
        is_vcf = True
        comment = None  # VCF用专门的函数处理
    elif ".tsv" in suffixes or ".tab" in suffixes:
        sep = "\t"
    elif ".csv" in suffixes:
        sep = ","
    else:
        sep = r"\s+"  # 默认空白符

    return sep, compression, comment, is_vcf


def standardize_columns(
    df: pd.DataFrame,
    column_mapping: Optional[Dict[str, str]] = None,
    custom_patterns: Optional[Dict[str, re.Pattern]] = None,
    keep_unmatched: bool = False,
) -> pd.DataFrame:
    """
    标准化DataFrame的列名

    Args:
        df: 原始DataFrame
        column_mapping: 手动指定的列名映射字典 {原始列名: 标准列名}
        custom_patterns: 自定义的正则表达式模式
        keep_unmatched: 是否保留未匹配的列

    Returns:
        标准化后的DataFrame
    """
    result_df = pd.DataFrame()

    # 如果提供了手动映射，先应用
    if column_mapping:
        for original_col, std_col in column_mapping.items():
            if original_col in df.columns:
                result_df[std_col] = df[original_col]

    # 自动匹配剩余列
    remaining_cols = [col for col in df.columns if col not in (column_mapping or {})]
    if remaining_cols:
        col_std = match_columns(remaining_cols, custom_patterns)

        for original_col, std_col in col_std.items():
            if std_col is not None:
                # 避免重复列
                if std_col not in result_df.columns:
                    result_df[std_col] = df[original_col]
            elif keep_unmatched:
                result_df[original_col] = df[original_col]

    return result_df


def add_metadata(df: pd.DataFrame, metadata: Dict[str, any]) -> pd.DataFrame:
    """
    向DataFrame添加元数据列

    Args:
        df: DataFrame
        metadata: 元数据字典 {列名: 值}

    Returns:
        添加元数据后的DataFrame
    """
    df_copy = df.copy()
    for key, value in metadata.items():
        df_copy[key] = value
    return df_copy


def convert_single_file(
    filename: str,
    sep: Optional[str] = None,
    compression: Optional[str] = None,
    comment: Optional[str] = None,
    column_mapping: Optional[Dict[str, str]] = None,
    custom_patterns: Optional[Dict[str, re.Pattern]] = None,
    metadata: Optional[Dict[str, any]] = None,
    keep_unmatched: bool = False,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    转换单个遗传学数据文件到标准化格式

    Args:
        filename: 文件路径
        sep: 分隔符，如果为None则自动检测
        compression: 压缩格式，如果为None则自动检测
        comment: 注释符号，如果为None则自动检测
        column_mapping: 手动指定的列名映射
        custom_patterns: 自定义的正则表达式模式
        metadata: 要添加的元数据
        keep_unmatched: 是否保留未匹配的列
        verbose: 是否打印详细信息

    Returns:
        标准化后的DataFrame
    """
    if verbose:
        print(f"\nProcessing file: {filename}")

    # 自动检测文件格式
    auto_sep, auto_compression, auto_comment, is_vcf = detect_file_format(filename)
    sep = sep or auto_sep
    compression = compression or auto_compression
    comment = comment if comment is not None else auto_comment

    if verbose:
        print(
            f"  Detected format: sep={repr(sep)}, compression={compression}, is_vcf={is_vcf}"
        )

    # 读取数据
    df = read_data(
        filename, sep=sep, compression=compression, comment=comment, is_vcf=is_vcf
    )

    if verbose:
        print(f"  Original shape: {df.shape}")
        print(f"  Original columns: {df.columns.tolist()}")

    # 标准化列名
    standardized_df = standardize_columns(
        df,
        column_mapping=column_mapping,
        custom_patterns=custom_patterns,
        keep_unmatched=keep_unmatched,
    )

    # 添加元数据
    if metadata:
        standardized_df = add_metadata(standardized_df, metadata)
        if verbose:
            print(f"  Added metadata: {list(metadata.keys())}")

    if verbose:
        print(f"  Standardized shape: {standardized_df.shape}")
        print(f"  Standardized columns: {standardized_df.columns.tolist()}")

    return standardized_df


def convert_from_metadata(
    metadata_df: pd.DataFrame,
    file_column: str = "file",
    metadata_columns: Optional[List[str]] = None,
    sep: Optional[str] = None,
    compression: Optional[str] = None,
    comment: Optional[str] = None,
    column_mapping: Optional[Dict[str, Dict[str, str]]] = None,
    custom_patterns: Optional[Dict[str, re.Pattern]] = None,
    keep_unmatched: bool = False,
    verbose: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    根据元数据表批量转换遗传学数据文件

    Args:
        metadata_df: 元数据DataFrame，必须包含文件路径列
        file_column: 文件路径列名
        metadata_columns: 要作为元数据添加到结果中的列名列表，如果为None则添加除文件路径外的所有列
        sep: 分隔符，如果为None则自动检测
        compression: 压缩格式，如果为None则自动检测
        comment: 注释符号，如果为None则自动检测
        column_mapping: 文件特定的列名映射 {文件路径: {原始列名: 标准列名}}
        custom_patterns: 自定义的正则表达式模式
        keep_unmatched: 是否保留未匹配的列
        verbose: 是否打印详细信息

    Returns:
        字典，键为文件路径，值为标准化后的DataFrame
    """
    if file_column not in metadata_df.columns:
        raise ValueError(f"Column '{file_column}' not found in metadata DataFrame")

    # 确定要添加的元数据列
    if metadata_columns is None:
        metadata_columns = [col for col in metadata_df.columns if col != file_column]

    result_dict = {}

    for idx, row in metadata_df.iterrows():
        filename = row[file_column]

        # 准备元数据
        file_metadata = {col: row[col] for col in metadata_columns}

        # 获取文件特定的列名映射
        file_mapping = column_mapping.get(filename) if column_mapping else None

        try:
            # 转换文件
            df = convert_single_file(
                filename=filename,
                sep=sep,
                compression=compression,
                comment=comment,
                column_mapping=file_mapping,
                custom_patterns=custom_patterns,
                metadata=file_metadata,
                keep_unmatched=keep_unmatched,
                verbose=verbose,
            )

            result_dict[filename] = df

        except Exception as e:
            print(f"  Error processing {filename}: {str(e)}")
            if verbose:
                import traceback

                traceback.print_exc()
            continue

    return result_dict


def convert_multiple_files(
    file_list: List[str],
    sep: Optional[str] = None,
    compression: Optional[str] = None,
    comment: Optional[str] = None,
    column_mapping: Optional[Dict[str, Dict[str, str]]] = None,
    custom_patterns: Optional[Dict[str, re.Pattern]] = None,
    metadata: Optional[Dict[str, Dict[str, any]]] = None,
    keep_unmatched: bool = False,
    verbose: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    批量转换多个遗传学数据文件

    Args:
        file_list: 文件路径列表
        sep: 分隔符，如果为None则自动检测
        compression: 压缩格式，如果为None则自动检测
        comment: 注释符号，如果为None则自动检测
        column_mapping: 文件特定的列名映射 {文件路径: {原始列名: 标准列名}}
        custom_patterns: 自定义的正则表达式模式
        metadata: 文件特定的元数据 {文件路径: {列名: 值}}
        keep_unmatched: 是否保留未匹配的列
        verbose: 是否打印详细信息

    Returns:
        字典，键为文件路径，值为标准化后的DataFrame
    """
    result_dict = {}

    for filename in file_list:
        # 获取文件特定的映射和元数据
        file_mapping = column_mapping.get(filename) if column_mapping else None
        file_metadata = metadata.get(filename) if metadata else None

        try:
            df = convert_single_file(
                filename=filename,
                sep=sep,
                compression=compression,
                comment=comment,
                column_mapping=file_mapping,
                custom_patterns=custom_patterns,
                metadata=file_metadata,
                keep_unmatched=keep_unmatched,
                verbose=verbose,
            )

            result_dict[filename] = df

        except Exception as e:
            print(f"  Error processing {filename}: {str(e)}")
            if verbose:
                import traceback

                traceback.print_exc()
            continue

    return result_dict


def save_results(
    result_dict: Dict[str, pd.DataFrame],
    output_dir: str,
    file_prefix: str = "standardized",
    file_suffix: str = "",
    output_format: str = "tsv",
    compression: Optional[str] = "gzip",
) -> None:
    """
    保存转换结果到文件

    Args:
        result_dict: 转换结果字典 {文件路径: DataFrame}
        output_dir: 输出目录
        file_prefix: 输出文件前缀
        file_suffix: 输出文件后缀
        output_format: 输出格式 ('tsv', 'csv', 'parquet')
        compression: 压缩格式
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for idx, (original_file, df) in enumerate(result_dict.items()):
        # 生成输出文件名
        base_name = Path(original_file).stem.split(".")[0]  # 去掉所有扩展名
        output_filename = f"{file_prefix}_{base_name}{file_suffix}"

        if output_format == "tsv":
            ext = ".tsv.gz" if compression == "gzip" else ".tsv"
            output_file = output_path / f"{output_filename}{ext}"
            df.to_csv(output_file, sep="\t", index=False, compression=compression)
        elif output_format == "csv":
            ext = ".csv.gz" if compression == "gzip" else ".csv"
            output_file = output_path / f"{output_filename}{ext}"
            df.to_csv(output_file, index=False, compression=compression)
        elif output_format == "parquet":
            output_file = output_path / f"{output_filename}.parquet"
            df.to_parquet(output_file, compression=compression or "snappy")
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        print(f"Saved: {output_file}")
