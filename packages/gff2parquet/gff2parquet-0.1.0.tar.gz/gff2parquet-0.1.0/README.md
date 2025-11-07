# gff2parquet

CLI tool for working with GFF3 genomic annotation files using Polars + Polars-bio for evaluation and processing.

## features

- **Convert** GFF3 files to Parquet, CSV, or JSON formats
- **Merge** multiple GFF files with optional column normalization
- **Filter** features by type, strand, length, sequence ID, and more
- **Split** annotations into separate files by any column
- **Extract** sequences from FASTA files based on GFF coordinates
- **Translate** CDS sequences to proteins with configurable genetic codes
- **Lazy evaluation** for memory-efficient processing of large datasets
- **Glob pattern support** for batch processing multiple files

## Installation
using (pixi)[https://pixi.sh/latest/] (recommended)
```bash
pixi install
```
Or with pip:
```
pip install . -e 
```

## Dependencies:
Base:
- python >= 3.9
- [polars](https://www.pola.rs/)
- [polars-bio](https://github.com/biodatageeks/polars-bio)  
For the [example notebook](data/example.ipynb), you will also need:
- [ipykernel](https://github.com/ipython/ipykernel)
- [jupyter](https://jupyter.org/)
- [jupyterlab](https://jupyterlab.readthedocs.io/en/stable/)
- [pyarrow](https://arrow.apache.org/docs/python/index.html) (only really used to get the parquets metadata)
- [ncbi-datasets](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/reference-docs/command-line/datasets/) (for downloading example datasets, although some are already included)

## Quick Start
See [example notebook](data/example.ipynb) for some more examples...
### Convert GFF to Parquet
```bash
# Single file
gff2parquet convert annotations.gff3 -o annotations.parquet

# Multiple files with glob pattern
gff2parquet convert "data/*.gff3" -o combined.parquet

# Normalize column names and shift coordinates
gff2parquet convert input.gff3 --normalize --shift-start 1 -o output.parquet
```

### Filter Features
```bash
# Extract CDS features longer than 500bp
gff2parquet filter annotations.gff3 --type CDS --min-length 500 -o long_cds.csv

# Filter by strand and sequence
gff2parquet filter input.gff3 --seqid chr1 --strand + -o chr1_plus.parquet
```

### Merge Multiple Files
```bash
# Merge all GFF files in a directory
gff2parquet merge "samples/*.gff3" -o merged.parquet

# Merge with normalization
gff2parquet merge file1.gff3 file2.gff3 --normalize -o combined.parquet


### Extract & Translate Sequences
```bash
# Extract CDS sequences as nucleotides
gff2parquet extract annotations.gff3 genome.fasta --type CDS -o cds.fasta

# Extract and translate to proteins (bacterial genetic code)
gff2parquet extract annotations.gff3 genome.fasta --type CDS --outaa amino -o proteins.fasta

# Extract from multiple genomes with custom genetic code
gff2parquet extract "*.gff3" genome*.fasta --outaa amino --genetic-code 2 -o mito_proteins.fasta
```

### Split by Column
```bash
# Split by feature type
gff2parquet split annotations.gff3 --column type --output-dir by_type/ -f gff

# Split by chromosome
gff2parquet split annotations.gff3 --column seqid --output-dir by_chr/ -f parquet
```

### Inspect Data
```bash
# View first 10 rows
gff2parquet print annotations.gff3 --head 10

# Show statistics
gff2parquet print annotations.gff3 --stats

# Filter and display specific columns
gff2parquet print annotations.gff3 --type gene --columns seqid,start,end,strand -f csv
```

## Common Workflows

### Multi-step Analysis Pipeline
```bash
# 1. Merge multiple samples
gff2parquet merge sample*.gff3 -o all_samples.parquet

# 2. Filter for long CDS features
gff2parquet filter all_samples.parquet --type CDS --min-length 600 -o long_cds.gff -f gff

# 3. Extract and translate sequences
gff2parquet extract long_cds.gff genome*.fasta --outaa amino -o proteins.fasta
```

### Quality Control
```bash
# Check feature distribution
gff2parquet print annotations.gff3 --stats

# Extract short features for inspection
gff2parquet filter annotations.gff3 --max-length 50 -o short_features.csv
```

## Output Formats

- **Parquet**: The answer to all your problem.
- **CSV/TSV**: Human-readable, but (polars) csv doesn't support nested data types so the attribute field is smushed together into string.
- **GFF3**: Standard genomic annotation format. The Attribute field is annoying.
- **JSONL**: probably not very useful, untested
- **FASTA**: what most bioinformatics tools use

## Genetic Codes

Use `--genetic-code` with extract command:

- `1` - Standard (default for most organisms)
- `2` - Vertebrate Mitochondrial
- `11` - Bacterial and Plant Plastid (default)

[Full list](https://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi)

## Advanced Features

### Streaming Mode - UNTESTED
For very large files that don't fit in memory:
```bash
gff2parquet convert huge_file.gff3 --streaming -o output.parquet
```

### Coordinate Shifting (USE WITH CAUTION)
Convert between 0-based and 1-based coordinates:
```bash
gff2parquet convert input.gff3 --shift-start 1 --shift-end 0 -o corrected.parquet
```

### Output to stdout (DOESN'T WORK FOR ALL COMMANDS)
```bash
gff2parquet filter input.gff3 --type CDS -o stdout #| grep "gene_id"
```

## Tips
- Use **glob patterns** for batch processing: `"data/*.gff3"` or `"sample_*.gff"`
- Use **Parquet format** for support of modern stuff.
- **Stream large files** with `--streaming` to reduce memory usage (untested)
- **Auto-format detection**: Output format detected from file extension unless `-f` specified (not for all commands)
- can be piped to other commands: 
```bash
[uneri]$ gff2parquet print data/downloaded_gff/groupI_GCA_000859985.2.gff --head 10   | grep "repeat"
Found 1 file(s) matching pattern 'data/downloaded_gff/groupI_GCA_000859985.2.gff'
Scanning: data/downloaded_gff/groupI_GCA_000859985.2.gff
| JN555585.1 | Genbank | inverted_repeat | 1     | 9213   | null  | +      | null  | [{"ID","id-JN555585.1:1..9213"}, {"Note","TRL%3B inverted repeat flanking UL"}, … {"rpt_type","inverted"}] | data/downloaded_gff/groupI_GCA_000859985.2.gff |
| JN555585.1 | Genbank | repeat_region   | 1     | 399    | null  | +      | null  | [{"ID","id-JN555585.1:1..399"}, {"Note","'a' sequence"}, … {"rpt_type","terminal"}]                        | data/downloaded_gff/groupI_GCA_000859985.2.gff |
| JN555585.1 | Genbank | repeat_region   | 98    | 320    | null  | +      | null  | [{"ID","id-JN555585.1:98..320"}, {"Note","'a' sequence reiteration set"}, … {"rpt_unit_range","98..109"}]  | data/downloaded_gff/groupI_GCA_000859985.2.gff |
```

## Development

### Using Pixi 
Default environment (minimal)
```bash
pixi install
pixi shell
```
Notebook environment (includes Jupyter):
```bash
pixi install -e notebook
pixi run -e notebook jupyter lab
```

## License
See LICENSE file.

## Citation
Neri and the gang
