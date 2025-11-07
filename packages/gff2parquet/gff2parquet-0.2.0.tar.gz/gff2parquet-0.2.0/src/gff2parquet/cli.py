#!/usr/bin/env python3
"""
GFF3 to Parquet conversion and manipulation tool.

This CLI tool provides various operations on GFF3 files using Polars for efficient processing.
Supports lazy evaluation for handling multiple files and large datasets.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Union
import polars as pl
from typing import Tuple, Dict
import polars_bio as pb


DEFAULT_CODE = 1
DEFAULT_FRAME = 1
DEFAULT_PMODE = 0
DEFAULT_NMODE = 0
DEFAULT_LMIN = 16
DEFAULT_IDWRD = 2
DEFAULT_DELIM = r"[ ,;:|]"
DEFAULT_UPPER = False

GENETIC_CODES_AA = {
    "1": "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "2": "FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNKKSS**VVVVAAAADDEEGGGG",
    "3": "FFLLSSSSYY**CCWWTTTTPPPPHHQQRRRRIIMMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "4": "FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "5": "FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNKKSSSSVVVVAAAADDEEGGGG",
    "6": "FFLLSSSSYYQQCC*WLLLLPPPPHHQQRRRRIIIMTTTTNKKSSRRVVVVAAAADDEEGGGG",
    "9": "FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNNKSSSSVVVVAAAADDEEGGGG",
    "10": "FFLLSSSSYY**CCCWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "11": "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "12": "FFLLSSSSYY**CC*WLLLSPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "13": "FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNKKSSGGVVVVAAAADDEEGGGG",
    "14": "FFLLSSSSYYY*CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNNKSSSSVVVVAAAADDEEGGGG",
    "15": "FFLLSSSSYY*QCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "16": "FFLLSSSSYY*LCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "21": "FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIMMTTTTNNNKSSSSVVVVAAAADDEEGGGG",
    "22": "FFLLSS*SYY*LCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "23": "FF*LSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "24": "FFLLSSSSYY**CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSSKVVVVAAAADDEEGGGG",
    "25": "FFLLSSSSYY**CCGWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "26": "FFLLSSSSYY**CC*WLLLAPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "27": "FFLLSSSSYYQQCCWWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "28": "FFLLSSSSYYQQCCWWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "29": "FFLLSSSSYYYYCC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "30": "FFLLSSSSYYEECC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "31": "FFLLSSSSYYEECCWWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
    "33": "FFLLSSSSYYY*CCWWLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSSKVVVVAAAADDEEGGGG",
}

GENETIC_CODES_START = {
    "1": "---M---------------M---------------M----------------------------",
    "2": "--------------------------------MMMM---------------M------------",
    "3": "----------------------------------MM----------------------------",
    "4": "--MM---------------M------------MMMM---------------M------------",
    "5": "---M----------------------------MMMM---------------M------------",
    "6": "-----------------------------------M----------------------------",
    "9": "-----------------------------------M---------------M------------",
    "10": "-----------------------------------M----------------------------",
    "11": "---M---------------M------------MMMM---------------M------------",
    "12": "-------------------M---------------M----------------------------",
    "13": "-----------------------------------M----------------------------",
    "14": "-----------------------------------M----------------------------",
    "15": "-----------------------------------M----------------------------",
    "16": "-----------------------------------M----------------------------",
    "21": "-----------------------------------M---------------M------------",
    "22": "-----------------------------------M----------------------------",
    "23": "--------------------------------M--M---------------M------------",
    "24": "---M---------------M---------------M---------------M------------",
    "25": "---M-------------------------------M---------------M------------",
    "26": "-------------------M---------------M----------------------------",
    "27": "-----------------------------------M----------------------------",
    "28": "-----------------------------------M----------------------------",
    "29": "-----------------------------------M----------------------------",
    "30": "-----------------------------------M----------------------------",
    "31": "-----------------------------------M----------------------------",
    "33": "---M---------------M---------------M---------------M------------",
}

NT_NAME = "TCAG"

def make_translation_table(genetic_code: int) -> Tuple[Dict[str, str], Dict[str, bool]]:
    """Create codon translation and start codon lookup tables."""
    code_str = str(genetic_code)
    if code_str not in GENETIC_CODES_AA:
        raise ValueError(f"Unknown genetic code: {genetic_code}")
    
    aa_string = GENETIC_CODES_AA[code_str]
    start_string = GENETIC_CODES_START[code_str]
    
    tranaa = {}
    transt = {}
    
    # Build codon tables
    for i in range(4):
        for j in range(4):
            for k in range(4):
                codon = NT_NAME[i] + NT_NAME[j] + NT_NAME[k]
                idx = i * 16 + j * 4 + k
                tranaa[codon] = aa_string[idx]
                transt[codon] = start_string[idx] != "-"
    
    tranaa["---"] = "-"
    return tranaa, transt


def translate_sequence(seq: str, genetic_code: int = 11, reverse_complement: bool = False) -> str:
    """Translate a nucleotide sequence to amino acids.
    
    Args:
        seq: DNA sequence (uppercase, T not U)
        genetic_code: Genetic code table to use
        reverse_complement: If True, reverse complement before translation
        
    Returns:
        Translated amino acid sequence
    """
    tranaa, transt = make_translation_table(genetic_code)
    
    # Handle reverse complement
    if reverse_complement:
        seq = seq[::-1]  # reverse
        seq = seq.translate(str.maketrans("AGCT", "TCGA"))  # complement
    
    translated = ""
    for i in range(0, len(seq) - 2, 3):
        codon = seq[i:i+3]
        aa = tranaa.get(codon, "X")
        translated += aa
    
    return translated


def extract_sequences_from_gff(
    gff_lf: pl.LazyFrame,
    fasta_files: List[str],
    output_type: str = "nucleic",
    genetic_code: int = 11
) -> pl.DataFrame:
    """Extract sequences from FASTA files based on GFF coordinates.
    
    Args:
        gff_lf: LazyFrame with GFF annotations
        fasta_files: List of FASTA file paths
        output_type: "nucleic" or "amino" for translation
        genetic_code: Genetic code for translation
        
    Returns:
        DataFrame with extracted sequences
    """
    # Load FASTA file(s)
    print("Loading FASTA sequences...", file=sys.stderr)
    fasta_dfs = []
    for fasta_file in fasta_files:
        print(f"  Reading: {fasta_file}", file=sys.stderr)
        fasta_df = pb.scan_fasta(fasta_file).collect()
        fasta_dfs.append(fasta_df)
    
    fasta_df = pl.concat(fasta_dfs, how="diagonal")
    
    # Collect GFF data
    gff_df = gff_lf.collect()
    
    print(f"Extracting {len(gff_df)} features...", file=sys.stderr)
    
    # Join GFF with FASTA to get sequences
    result_df = gff_df.join(
        fasta_df.select(["name", "sequence"]),
        left_on="seqid",
        right_on="name",
        how="inner"
    )
    
    # Extract subsequences based on coordinates
    def extract_subseq(row):
        seq = row["sequence"]
        start = row["start"] - 1  # Convert to 0-based
        end = row["end"]
        strand = row.get("strand", "+")
        
        subseq = seq[start:end]
        
        # Handle reverse strand
        if strand == "-":
            subseq = subseq[::-1]  # reverse
            subseq = subseq.translate(str.maketrans("AGCT", "TCGA"))  # complement
        
        # Translate if needed
        if output_type == "amino":
            subseq = translate_sequence(subseq, genetic_code, reverse_complement=False)
        
        return subseq
    
    # Extract sequences
    extracted_seqs = []
    for row in result_df.iter_rows(named=True):
        extracted_seqs.append(extract_subseq(row))
    
    result_df = result_df.with_columns(
        pl.Series("extracted_sequence", extracted_seqs)
    )
    
    return result_df


def write_fasta(df: pl.DataFrame, output_file: Union[str, Path], 
                seq_column: str = "extracted_sequence",
                id_columns: Optional[List[str]] = None,
                n_buffer: int = -1):
    """Write DataFrame to FASTA format.
    
    Args:
        df: DataFrame with sequences
        output_file: Output file path or stdout
        seq_column: Column containing sequences
        id_columns: Columns to use for FASTA headers (default: seqid, type, start, end, strand)
        n_buffer: Number of characters to wrap sequences at (people like 60 or 80, but the default is -1 to disable)
    """
    if id_columns is None:
        id_columns = ["seqid", "type", "start", "end", "strand"]
    
    # Build FASTA headers
    def build_header(row):
        parts = []
        for col in id_columns:
            if col in row:
                parts.append(f"{row[col]}")
        return "__".join(str(p) for p in parts)
    
    use_stdout = output_file in ['-', 'stdout'] or output_file is None
    
    if use_stdout:
        f = sys.stdout
    else:
        f = open(output_file, 'w')
    
    try:
        for row in df.iter_rows(named=True):
            header = build_header(row)
            seq = row[seq_column]
            
            # Write FASTA entry
            f.write(f">{header}\n")
            if n_buffer > 0:
                # Wrap sequence at n_buffer characters
                for i in range(0, len(seq), n_buffer):
                    f.write(seq[i:i+n_buffer] + "\n")
            else:
                f.write(seq + "\n")
    
    finally:
        if not use_stdout:
            f.close()


def cmd_extract(args):
    """Extract sequences from FASTA based on GFF annotations."""
    if pb is None:
        print("Error: polars_bio is required for extract command", file=sys.stderr)
        print("Install with: pip install polars-bio", file=sys.stderr)
        sys.exit(1)
    
    # Load GFF
    print(f"Loading GFF from: {args.gff}", file=sys.stderr)
    lf = scan_gff_files(args.gff)
    
    # Apply filters if specified
    if any([args.type, args.seqid, args.strand, args.min_length, args.max_length, args.name_contains]):
        print("Applying filters...", file=sys.stderr)
        lf = filter_features(
            lf,
            feature_type=args.type,
            seqid=args.seqid,
            min_length=args.min_length,
            max_length=args.max_length,
            strand=args.strand
        )
        
        # Name/ID filter
        if args.name_contains:
            lf = lf.filter(
                pl.col("attributes").str.contains(args.name_contains, literal=False)
            )
    
    # Expand glob patterns for FASTA files
    from pathlib import Path
    fasta_files = []
    for pattern in args.fasta:
        matched = list(Path().glob(pattern))
        if matched:
            fasta_files.extend([str(p) for p in matched])
        else:
            # If no match, treat as literal filename (might exist or error later)
            fasta_files.append(pattern)
    
    if not fasta_files:
        print("Error: No FASTA files found", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(fasta_files)} FASTA file(s)", file=sys.stderr)
    
    # Extract sequences
    result_df = extract_sequences_from_gff(
        lf,
        fasta_files,
        output_type=args.outaa,
        genetic_code=args.genetic_code
    )
    
    print(f"Extracted {len(result_df)} sequences", file=sys.stderr)
    
    # Write output
    if args.format == "fasta":
        write_fasta(result_df, args.output, id_columns=args.id_columns)
        print("Done!", file=sys.stderr)
    elif args.format == "csv":
        use_stdout = args.output in ['-', 'stdout', None]
        if use_stdout:
            sys.stdout.write(result_df.write_csv(separator="\t"))
        else:
            result_df.write_csv(args.output, separator="\t")
        print("Done!", file=sys.stderr)
    elif args.format == "parquet":
        if args.output in ['-', 'stdout', None]:
            print("Error: Cannot write Parquet to stdout", file=sys.stderr)
            sys.exit(1)
        result_df.write_parquet(args.output)
        print("Done!", file=sys.stderr)



def from_gff_lazy(input_file: Union[str, Path]) -> pl.LazyFrame:
    """Scan a gff(3) file into a lazy polars DataFrame.

    Args:
        input_file (Union[str, Path]): Path to the GFF3 file

    Returns:
        pl.LazyFrame: Lazy DataFrame with columns as gff3 specs.
    """
    schema = pl.Schema([
        ('seqid', pl.String),
        ('source', pl.String),
        ('type', pl.String),
        ('start', pl.UInt32),
        ('end', pl.UInt32),
        ('score', pl.Float32),
        ('strand', pl.String),
        ('phase', pl.UInt32),
        ('attributes', pl.String)
    ])
    
    reader = pl.scan_csv(
        input_file, 
        has_header=False, 
        separator="\t", 
        comment_prefix="#", 
        schema=schema,
        null_values=["."]
    )
    
    # Parse attributes into structured format
    # Format: key1=value1;key2=value2;...
    reader = reader.with_columns(
        pl.col("attributes").str.split(";").alias("attributes_list")
    ).with_columns(
        pl.col("attributes_list").list.eval(
            pl.element().str.split_exact("=", 1).struct.rename_fields(["key", "value"])
        ).alias("attributes")
    ).drop("attributes_list")
    
    return reader

def normalize_column_names(df):
    """Normalize common column name variations to standard names.
    
    Maps various column names to standard annotation schema:
    - begin/from/seq_from -> start
    - to/seq_to -> end  
    - qseqid/sequence_ID/contig_id -> sequence_id
    - etc.
    """
    
    # Define column name mappings
    column_mappings = {
        # Start position variations
        'begin': 'start',
        'from': 'start', 
        'seq_from': 'start',
        'query_start': 'start',
        'qstart': 'start',
        
        # End position variations
        'to': 'end',
        'seq_to': 'end',
        'query_end': 'end',
        'qend': 'end',
        
        # Sequence ID variations
        'qseqid': 'sequence_id',
        'sequence_ID': 'sequence_id',
        'contig_id': 'sequence_id',
        'contig': 'sequence_id',
        'query': 'sequence_id',
        'id': 'sequence_id',
        'name': 'sequence_id',
        
        # Score variations
        'bitscore': 'score',
        'bit_score': 'score',
        'bits': 'score',
        'evalue': 'evalue',
        'e_value': 'evalue',
        
        # Source variations
        'tool': 'source',
        'method': 'source',
        'db': 'source',
        'database': 'source',
        
        # Type variations
        'feature': 'type',
        'annotation': 'type',
        'category': 'type',
    }
    
    # Rename columns if they exist
    rename_dict = {}
    for old_name, new_name in column_mappings.items():
        if old_name in df.columns:
            rename_dict[old_name] = new_name
    
    if rename_dict:
        df = df.rename(rename_dict)
    
    return df


def scan_gff_files(pattern: str) -> pl.LazyFrame:
    """Scan multiple GFF or Parquet files matching a glob pattern.
    
    Args:
        pattern: Glob pattern for files (e.g., "*.gff3", "*.parquet", or "data/**/*.gff")
        
    Returns:
        Combined LazyFrame from all matching files
    """
    from pathlib import Path
    
    paths = list(Path().glob(pattern))
    
    if not paths:
        raise FileNotFoundError(f"No files found matching pattern: {pattern}")
    
    print(f"Found {len(paths)} file(s) matching pattern '{pattern}'", file=sys.stderr)
    
    # Scan all files and concatenate
    lazyframes = []
    for path in paths:
        print(f"Scanning: {path}", file=sys.stderr)
        
        # Determine file type by extension
        ext = path.suffix.lower()
        
        if ext in ['.parquet', '.pq']:
            # Read Parquet file
            lf = pl.scan_parquet(str(path))
        elif ext in ['.gff', '.gff3', '.gtf']:
            # Read GFF file
            lf = from_gff_lazy(str(path))
            # Add source file column
            lf = lf.with_columns(pl.lit(str(path)).alias("source_file"))
        else:
            # Default to GFF format
            print(f"Warning: Unknown extension '{ext}', treating as GFF", file=sys.stderr)
            lf = from_gff_lazy(str(path))
            # Add source file column
            lf = lf.with_columns(pl.lit(str(path)).alias("source_file"))
        
        lazyframes.append(lf)
    
    return pl.concat(lazyframes, how="diagonal")


def normalize_gff(lf: pl.LazyFrame) -> pl.LazyFrame:
    """Normalize GFF column names to standard schema.
    
    Args:
        lf: Input LazyFrame
        
    Returns:
        LazyFrame with normalized column names
    """
    # Collect, normalize, then convert back to lazy
    # (normalize_column_names expects eager DataFrame)
    df = lf.collect()
    df = normalize_column_names(df)
    return df.lazy()


def shift_coordinates(
    lf: pl.LazyFrame,
    shift_start: int = 0,
    shift_end: int = 0
) -> pl.LazyFrame:
    """Shift start and/or end coordinates by specified amounts.
    
    Args:
        lf: Input LazyFrame
        shift_start: Amount to shift start coordinate
        shift_end: Amount to shift end coordinate
        
    Returns:
        LazyFrame with shifted coordinates
    """
    exprs = []
    
    if shift_start != 0:
        exprs.append((pl.col("start") + shift_start).alias("start"))
    
    if shift_end != 0:
        exprs.append((pl.col("end") + shift_end).alias("end"))
    
    if exprs:
        return lf.with_columns(exprs)
    
    return lf


def merge_gff_files(patterns: List[str]) -> pl.LazyFrame:
    """Merge multiple GFF files from patterns.
    
    Args:
        patterns: List of file patterns to merge
        
    Returns:
        Combined LazyFrame from all matching files
    """
    all_lazyframes = []
    
    for pattern in patterns:
        lf = scan_gff_files(pattern)
        all_lazyframes.append(lf)
    
    if not all_lazyframes:
        raise ValueError("No files found to merge")
    
    return pl.concat(all_lazyframes, how="diagonal")


def split_by_column(
    lf: pl.LazyFrame,
    column: str,
    output_dir: Path,
    output_format: str = "parquet"
) -> None:
    """Split GFF data into separate files based on column values.
    
    Args:
        lf: Input LazyFrame
        column: Column to split by
        output_dir: Directory for output files
        output_format: Output format ('parquet', 'csv', or 'gff')
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Collect to get unique values
    df = lf.collect()
    unique_values = df[column].unique().to_list()
    
    print(f"Splitting into {len(unique_values)} files by '{column}'", file=sys.stderr)
    
    for value in unique_values:
        # Filter for this value
        subset = df.filter(pl.col(column) == value)
        
        # Sanitize filename
        safe_value = str(value).replace("/", "_").replace(" ", "_")
        
        if output_format == "parquet":
            output_file = output_dir / f"{column}_{safe_value}.parquet"
            subset.write_parquet(output_file)
        elif output_format == "csv":
            output_file = output_dir / f"{column}_{safe_value}.csv"
            subset.write_csv(output_file, separator="\t")
        elif output_format == "gff":
            output_file = output_dir / f"{column}_{safe_value}.gff3"
            write_gff(subset, output_file)
        
        print(f"Wrote {subset.height} rows to {output_file}", file=sys.stderr)

def write_gff(df: pl.DataFrame, output_file: Union[str, Path]) -> None:
    """Write DataFrame back to GFF3 format.
    
    Args:
        df: DataFrame to write
        output_file: Output file path
    """
    # Ensure required columns exist
    required_cols = ["seqid", "source", "type", "start", "end", "score", "strand", "phase", "attributes"]
    
    # Fill missing columns with defaults
    for col in required_cols:
        if col not in df.columns:
            if col in ["seqid", "source", "type", "strand"]:
                df = df.with_columns(pl.lit(".").alias(col))
            elif col in ["start", "end"]:
                df = df.with_columns(pl.lit(0).alias(col))
            elif col == "score":
                df = df.with_columns(pl.lit(".").alias(col))
            elif col == "phase":
                df = df.with_columns(pl.lit(".").alias(col))
            elif col == "attributes":
                df = df.with_columns(pl.lit(".").alias(col))
    
    # Convert attributes column if it's a list of structs
    if df.schema["attributes"] == pl.List(pl.Struct):
        df = df.with_columns(
            pl.col("attributes").list.eval(
                pl.concat_str([
                    pl.element().struct.field("key"),
                    pl.lit("="),
                    pl.element().struct.field("value")
                ])
            ).list.join(";").alias("attributes")
        )
    
    # Select and order columns
    df = df.select(required_cols)
    
    # Write with GFF3 header
    with open(output_file, 'w') as f:
        f.write("##gff-version 3\n")
        # Write the dataframe as CSV (tab-separated)
        csv_content = df.write_csv(separator="\t", include_header=False, quote_style="never")
        f.write(csv_content)

def write_output(lf: pl.LazyFrame, output: Optional[str], format: str, streaming: bool = False):
    """Write output to file or stdout.
    
    Args:
        lf: LazyFrame to write
        output: Output path or None/'-'/'stdout' for stdout
        format: Output format ('parquet', 'csv', 'gff', 'json')
        streaming: Use streaming mode
    Notes:
        - CSV does not support nested data types, which is what the attributes column usually contains. 
          As such, it is converted to a delimited string. You would need to parse it back on your own.
    """
    use_stdout = output is None or output in ['-', 'stdout']
    
    if format == "parquet":
        if use_stdout:
            print("Error: Cannot write Parquet to stdout", file=sys.stderr)
            sys.exit(1)
        
        print(f"Writing Parquet to {output}...", file=sys.stderr)
        if streaming:
            lf.sink_parquet(output)
        else:
            lf.collect().write_parquet(output)
    
    elif format == "csv":
        print("Writing CSV...", file=sys.stderr)
        
        # Convert attributes back to string format for CSV
        # attributes is List(Struct), need to convert to "key=value;key=value" format
        lf = lf.with_columns(
            pl.col("attributes").list.eval(
                pl.concat_str([
                    pl.element().struct.field("key"),
                    pl.lit("="),
                    pl.element().struct.field("value")
                ])
            ).list.join(";").alias("attributes")
        )
        
        if use_stdout:
            df = lf.collect()
            sys.stdout.write(df.write_csv(separator="\t"))
        elif streaming:
            lf.sink_csv(output, separator="\t")
        else:
            lf.collect().write_csv(output, separator="\t")
    
    elif format == "json":
        print("Writing JSON...", file=sys.stderr)
        
        df = lf.collect()
        
        if use_stdout:
            sys.stdout.write(df.write_json())
        else:
            df.write_json(output)
    
    elif format == "gff":
        if use_stdout:
            print("Error: Cannot write GFF to stdout (use CSV format instead)", file=sys.stderr)
            sys.exit(1)
        
        print(f"Writing GFF3 to {output}...", file=sys.stderr)
        df = lf.collect()
        write_gff(df, output)
    
    else:
        print(f"Error: Unknown format '{format}'", file=sys.stderr)
        sys.exit(1)

def filter_features(
    lf: pl.LazyFrame,
    feature_type: Optional[str] = None,
    seqid: Optional[str] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    strand: Optional[str] = None
) -> pl.LazyFrame:
    """Filter features based on various criteria.
    
    Args:
        lf: Input LazyFrame
        feature_type: Filter by feature type
        seqid: Filter by sequence ID
        min_length: Minimum feature length
        max_length: Maximum feature length
        strand: Filter by strand ('+', '-', or '.')
        
    Returns:
        Filtered LazyFrame
    """
    filters = []
    
    if feature_type:
        filters.append(pl.col("type") == feature_type)
    
    if seqid:
        filters.append(pl.col("seqid") == seqid)
    
    if strand:
        filters.append(pl.col("strand") == strand)
    
    if min_length is not None or max_length is not None:
        # Calculate length
        lf = lf.with_columns((pl.col("end") - pl.col("start") + 1).alias("length"))
        
        if min_length is not None:
            filters.append(pl.col("length") >= min_length)
        
        if max_length is not None:
            filters.append(pl.col("length") <= max_length)
    
    if filters:
        return lf.filter(pl.all_horizontal(filters))
    
    return lf


# Command handlers

def cmd_convert(args):
    """Convert GFF to Parquet/CSV."""
    lf = scan_gff_files(args.input)
    
    if args.normalize:
        print("Normalizing column names...", file=sys.stderr)
        lf = normalize_gff(lf)
    
    if args.shift_start != 0 or args.shift_end != 0:
        print(f"Shifting coordinates (start: {args.shift_start}, end: {args.shift_end})...", file=sys.stderr)
        lf = shift_coordinates(lf, args.shift_start, args.shift_end)
    
    write_output(lf, args.output, args.format, args.streaming)
    print("Done!", file=sys.stderr)


def cmd_merge(args):
    """Merge multiple GFF files."""
    print(f"Merging {len(args.inputs)} input pattern(s)...", file=sys.stderr)
    lf = merge_gff_files(args.inputs)
    
    if args.normalize:
        print("Normalizing column names...", file=sys.stderr)
        lf = normalize_gff(lf)
    
    write_output(lf, args.output, args.format, args.streaming)
    print("Done!", file=sys.stderr)


def cmd_filter(args):
    """Filter GFF features."""
    lf = scan_gff_files(args.input)
    
    print("Applying filters...", file=sys.stderr)
    lf = filter_features(
        lf,
        feature_type=args.type,
        seqid=args.seqid,
        min_length=args.min_length,
        max_length=args.max_length,
        strand=args.strand
    )
    
    # Determine output format
    output_format = args.format
    
    # Auto-detect from file extension if format not specified
    if output_format is None and args.output and args.output not in ['-', 'stdout']:
        from pathlib import Path
        ext = Path(args.output).suffix.lower()
        
        if ext == '.parquet':
            output_format = 'parquet'
        elif ext in ['.gff', '.gff3']:
            output_format = 'gff'
        elif ext in ['.csv', '.tsv', '.txt']:
            output_format = 'csv'
        elif ext == '.json':
            output_format = 'json'
    
    # Default to CSV if still not determined
    if output_format is None:
        output_format = 'csv'
    
    write_output(lf, args.output, output_format, args.streaming)
    print("Done!", file=sys.stderr)

def cmd_split(args):
    """Split GFF by column values."""
    lf = scan_gff_files(args.input)
    
    if args.column not in lf.collect_schema().names():
        print(f"Error: Column '{args.column}' not found", file=sys.stderr)
        sys.exit(1)
    
    split_by_column(lf, args.column, args.output_dir, args.format)
    print("Done!", file=sys.stderr)


def cmd_print(args):
    """Print GFF contents to stdout."""
    # first set polars config to display all columns and rows, and not wrap long lines
    pl.Config.set_tbl_rows(123123)
    pl.Config.set_tbl_cols(12313)
    pl.Config.set_fmt_str_lengths(2100) 
    pl.Config.set_tbl_width_chars(2100) 

    pl.Config.set_tbl_formatting("MARKDOWN")
    pl.Config.set_tbl_hide_dataframe_shape(True)


    lf = scan_gff_files(args.input)
    
    # Apply filters if specified
    if any([args.type, args.seqid, args.strand, args.min_length, args.max_length]):
        lf = filter_features(
            lf,
            feature_type=args.type,
            seqid=args.seqid,
            min_length=args.min_length,
            max_length=args.max_length,
            strand=args.strand
        )

        # Convert attributes for CSV format before collecting
    if args.format == 'csv':
        lf = lf.with_columns(
            pl.col("attributes").list.eval(
                pl.concat_str([
                    pl.element().struct.field("key"),
                    pl.lit("="),
                    pl.element().struct.field("value")
                ])
            ).list.join(";").alias("attributes")
        )
    
    df = lf.collect()
    
    # Apply head/tail if specified
    if args.head:
        df = df.head(args.head)
    elif args.tail:
        df = df.tail(args.tail)
    
    # Select columns if specified
    if args.columns:
        cols = [c.strip() for c in args.columns.split(',')]
        missing = [c for c in cols if c not in df.columns]
        if missing:
            print(f"Error: Columns not found: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
        df = df.select(cols)
    
    # Output format
    if args.format == 'table':
        print(df)
    elif args.format == 'json':
        sys.stdout.write(df.write_json())
    elif args.format == 'csv':
        sys.stdout.write(df.write_csv(separator="\t"))

    
    if args.stats:
        print("\n--- Statistics ---", file=sys.stderr)
        print(f"Total rows: {df.height}", file=sys.stderr)
        print(f"Total columns: {df.width}", file=sys.stderr)
        if 'type' in df.columns:
            print("\nFeature types:", file=sys.stderr)
            type_counts = df.group_by('type').agg(pl.count().alias('count')).sort('count', descending=True)
            print(type_counts, file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        description="GFF3 to Parquet conversion and manipulation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single GFF to Parquet
  %(prog)s convert input.gff3 -o output.parquet
  
  # Convert and output to stdout as CSV
  %(prog)s convert input.gff3 -f csv -o stdout
  
  # Merge multiple GFF files
  %(prog)s merge file1.gff3 file2.gff3 "data/*.gff3" -o combined.parquet
  
  # Normalize column names during conversion
  %(prog)s convert input.gff3 --normalize -o output.parquet
  
  # Shift coordinates (convert 0-based to 1-based)
  %(prog)s convert input.gff3 --shift-start 1 -o output.parquet
  
  # Filter features
  %(prog)s filter input.gff3 --type CDS --min-length 300 -o filtered.csv
  %(prog)s filter input.gff3 --seqid chr1 --strand + -o stdout
  
  # Split by feature type into separate files
  %(prog)s split input.gff3 --column type --output-dir split_files/
  
  # Print/inspect GFF data
  %(prog)s print input.gff3 --head 10
  %(prog)s print input.gff3 --type gene --stats
  %(prog)s print input.gff3 --columns seqid,type,start,end -f csv
  
  # Extract CDS sequences as nucleotides
  %(prog)s extract annotations.gff3 genome.fasta --type CDS -o cds.fasta
  
  # Extract and translate CDS to proteins
  %(prog)s extract annotations.gff3 genome.fasta --type CDS --outaa amino -o proteins.fasta
  
  # Extract with custom genetic code (mitochondrial)
  %(prog)s extract annotations.gff3 mitogenome.fasta --outaa amino --genetic-code 2 -o proteins.fasta
  
  # Extract genes containing "kinase" in annotations
  %(prog)s extract annotations.gff3 genome.fasta --name-contains kinase --type gene -o kinases.fasta
  
  # Extract from multiple genomes and save as parquet for analysis
  %(prog)s extract "*.gff3" genome1.fa genome2.fa -f parquet -o extracted.parquet
  
  # Combine operations: merge, filter, and extract
  %(prog)s merge sample*.gff3 -o merged.parquet
  %(prog)s filter merged.parquet --type CDS --min-length 500 -o long_cds.gff3 -f gff
  %(prog)s extract long_cds.gff3 genome.fasta --outaa amino -o long_proteins.fasta

Genetic Codes (for --genetic-code):
  1  - Standard (default for most organisms)
  2  - Vertebrate Mitochondrial
  3  - Yeast Mitochondrial
  4  - Mold/Protozoan/Coelenterate Mitochondrial
  5  - Invertebrate Mitochondrial
  6  - Ciliate/Dasycladacean/Hexamita Nuclear
  9  - Echinoderm/Flatworm Mitochondrial
  11 - Bacterial and Plant Plastid (default)
  
  See full list at: https://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi

Tips:
  - Use glob patterns for multiple files: "data/*.gff3" or "sample_*.gff"
  - Use "-" or "stdout" for -o to pipe output (CSV/FASTA only)
  - Combine with standard Unix tools: %(prog)s print input.gff3 -f csv | grep "kinase"
  - Use --streaming for very large files to reduce memory usage
  - Parquet format is much faster for large datasets and preserves data types
  - Use print command with --stats to get overview before processing
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    subparsers.required = True
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', 
        help='Convert GFF to Parquet/CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.gff3 -o output.parquet
  %(prog)s input.gff3 -f csv -o stdout | head -20
  %(prog)s "data/*.gff3" --normalize -o combined.parquet
  %(prog)s input.gff3 --shift-start 1 --shift-end 0 -o corrected.parquet
        """)
    convert_parser.add_argument('input', help='Input GFF3 file or glob pattern')
    convert_parser.add_argument('-o', '--output', help='Output file (use "-" or "stdout" for stdout with CSV)')
    convert_parser.add_argument('-f', '--format', choices=['parquet', 'csv', 'gff'], 
                               default='parquet', help='Output format (default: parquet)')
    convert_parser.add_argument('--normalize', action='store_true',
                               help='Normalize column names to standard schema')
    convert_parser.add_argument('--shift-start', type=int, default=0,
                               help='Shift start coordinates by N positions')
    convert_parser.add_argument('--shift-end', type=int, default=0,
                               help='Shift end coordinates by N positions')
    convert_parser.add_argument('--streaming', action='store_true',
                               help='Use streaming mode for large files')
    convert_parser.set_defaults(func=cmd_convert)
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', 
        help='Merge multiple GFF files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s file1.gff3 file2.gff3 -o merged.parquet
  %(prog)s sample*.gff3 "other/*.gff" -o all_annotations.parquet
  %(prog)s *.gff3 --normalize -f csv -o stdout
        """)
    merge_parser.add_argument('inputs', nargs='+', help='Input GFF3 files or glob patterns')
    merge_parser.add_argument('-o', '--output', help='Output file (use "-" or "stdout" for stdout with CSV)')
    merge_parser.add_argument('-f', '--format', choices=['parquet', 'csv', 'gff'],
                             default='parquet', help='Output format (default: parquet)')
    merge_parser.add_argument('--normalize', action='store_true',
                             help='Normalize column names to standard schema')
    merge_parser.add_argument('--streaming', action='store_true',
                             help='Use streaming mode for large files')
    merge_parser.set_defaults(func=cmd_merge)
    
    # Filter command
    filter_parser = subparsers.add_parser('filter', 
        help='Filter GFF features',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.gff3 --type CDS -o cds_only.gff3 -f gff
  %(prog)s input.gff3 --type gene --min-length 1000 -o long_genes.csv
  %(prog)s input.gff3 --seqid chromosome1 --strand + -o stdout
  %(prog)s input.gff3 --type exon --min-length 50 --max-length 500 -o filtered.parquet
        """)
    filter_parser.add_argument('input', help='Input GFF3 file or glob pattern')
    filter_parser.add_argument('-o', '--output', help='Output file (use "-" or "stdout" for stdout with CSV)')
    filter_parser.add_argument('-f', '--format', choices=['parquet', 'csv', 'gff', 'json'],
                          default=None, help='Output format (auto-detected from extension if not specified)')
    filter_parser.add_argument('--type', help='Filter by feature type')
    filter_parser.add_argument('--seqid', help='Filter by sequence ID')
    filter_parser.add_argument('--strand', choices=['+', '-', '.'], help='Filter by strand')
    filter_parser.add_argument('--min-length', type=int, help='Minimum feature length')
    filter_parser.add_argument('--max-length', type=int, help='Maximum feature length')
    filter_parser.add_argument('--streaming', action='store_true',
                              help='Use streaming mode for large files')
    filter_parser.set_defaults(func=cmd_filter)
    
    # Split command
    split_parser = subparsers.add_parser('split', 
        help='Split GFF by column values',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.gff3 --column type --output-dir by_type/
  %(prog)s input.gff3 --column seqid --output-dir by_chromosome/ -f gff
  %(prog)s input.gff3 --column source --output-dir by_source/ -f csv
        """)
    split_parser.add_argument('input', help='Input GFF3 file or glob pattern')
    split_parser.add_argument('-c', '--column', required=True, help='Column to split by')
    split_parser.add_argument('-d', '--output-dir', type=Path, default=Path('output'),
                             help='Output directory (default: output/)')
    split_parser.add_argument('-f', '--format', choices=['parquet', 'csv', 'gff'],
                             default='parquet', help='Output format (default: parquet)')
    split_parser.set_defaults(func=cmd_split)
    
    # Print command
    print_parser = subparsers.add_parser('print', 
        help='Print GFF contents to stdout',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.gff3 --head 20
  %(prog)s input.gff3 --type gene --stats
  %(prog)s input.gff3 --columns seqid,type,start,end,strand -f csv
  %(prog)s input.gff3 --type CDS --min-length 500 --tail 10 -f table
  %(prog)s input.gff3 --seqid chr1 -f json | jq .
        """)
    print_parser.add_argument('input', help='Input GFF3 file or glob pattern')
    print_parser.add_argument('-f', '--format', choices=['table', 'csv', 'json'],
                             default='table', help='Output format (default: table which is markdown) also the csv is actallty a tsv (tabs)')
    print_parser.add_argument('--head', type=int, help='Show first N rows')
    print_parser.add_argument('--tail', type=int, help='Show last N rows')
    print_parser.add_argument('--columns', help='Comma-separated list of columns to display')
    print_parser.add_argument('--stats', action='store_true', help='Show statistics')
    # Filter options for print
    print_parser.add_argument('--type', help='Filter by feature type')
    print_parser.add_argument('--seqid', help='Filter by sequence ID')
    print_parser.add_argument('--strand', choices=['+', '-', '.'], help='Filter by strand')
    print_parser.add_argument('--min-length', type=int, help='Minimum feature length')
    print_parser.add_argument('--max-length', type=int, help='Maximum feature length')
    print_parser.set_defaults(func=cmd_print)
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', 
        help='Extract sequences from FASTA based on GFF annotations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all CDS as nucleotides
  %(prog)s annotations.gff3 genome.fasta --type CDS -o cds.fasta
  
  # Extract and translate CDS to proteins (bacterial code)
  %(prog)s annotations.gff3 genome.fasta --type CDS --outaa amino -o proteins.fasta
  
  # Extract mitochondrial genes with mitochondrial genetic code
  %(prog)s mito.gff3 mitogenome.fasta --outaa amino --genetic-code 2 -o mito_proteins.fasta
  
  # Extract genes containing "kinase" in their name/attributes
  %(prog)s annotations.gff3 genome.fasta --name-contains kinase -o kinases.fasta
  
  # Extract from multiple genomes
  %(prog)s "*.gff3" genome1.fa genome2.fa -f parquet -o all_sequences.parquet
  
  # Custom FASTA headers
  %(prog)s annotations.gff3 genome.fasta --id-columns seqid start end type -o custom.fasta
  
  # Extract long CDS and translate
  %(prog)s annotations.gff3 genome.fasta --type CDS --min-length 500 --outaa amino -o long_proteins.fasta
        """)
    extract_parser.add_argument('gff', help='Input GFF3 file or glob pattern')
    extract_parser.add_argument('fasta', nargs='+', help='Input FASTA file(s)')
    extract_parser.add_argument('-o', '--output', help='Output file (use "-" or "stdout" for stdout with FASTA/CSV)')
    extract_parser.add_argument('-f', '--format', choices=['fasta', 'csv', 'parquet'],
                               default='fasta', help='Output format (default: fasta)')
    extract_parser.add_argument('--outaa', choices=['amino', 'nucleic'], default='nucleic',
                               help='Output amino acids (translate) or nucleic acids (default: nucleic)')
    extract_parser.add_argument('--genetic-code', type=int, default=11,
                               help='Genetic code for translation (default: 11 - Bacterial/Plastid)')
    extract_parser.add_argument('--id-columns', nargs='+',
                               default=['seqid', 'type', 'start', 'end', 'strand'],
                               help='Columns to use for FASTA headers (default: seqid type start end strand)')
    # Filter options
    extract_parser.add_argument('--type', help='Filter by feature type (e.g., CDS, gene)')
    extract_parser.add_argument('--seqid', help='Filter by sequence ID')
    extract_parser.add_argument('--strand', choices=['+', '-', '.'], help='Filter by strand')
    extract_parser.add_argument('--min-length', type=int, help='Minimum feature length')
    extract_parser.add_argument('--max-length', type=int, help='Maximum feature length')
    extract_parser.add_argument('--name-contains', help='Filter features containing this string in attributes/name')
    extract_parser.set_defaults(func=cmd_extract)
    
    args = parser.parse_args()
    
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
