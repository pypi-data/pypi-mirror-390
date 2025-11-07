#!/bin/bash
# Comprehensive test script for gff2parquet tool
# Tests all major features with the example datasets
cd /clusterfs/jgi/scratch/science/metagen/neri/code/blits/gff2parquet

pixi shell 
set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Setup
SCRIPT="python ../gff2parquet.py"  # Adjust path as needed
DATA_DIR="data"
GFF_DIR="${DATA_DIR}/downloaded_gff"
FASTA_DIR="${DATA_DIR}/downloaded_fasta"
OUTPUT_DIR="test_output"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}GFF2Parquet Comprehensive Test Suite${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Clean and create output directory
rm -rf ${OUTPUT_DIR}
mkdir -p ${OUTPUT_DIR}/{convert,merge,filter,split,print,extract}

# Test counter
TEST_NUM=0

print_test() {
    TEST_NUM=$((TEST_NUM + 1))
    echo -e "\n${GREEN}[Test ${TEST_NUM}] $1${NC}"
}

#==============================================================================
# CONVERT COMMAND TESTS
#==============================================================================
echo -e "\n${YELLOW}=== CONVERT COMMAND TESTS ===${NC}"

print_test "Convert single GFF to Parquet"
${SCRIPT} convert ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    -o ${OUTPUT_DIR}/convert/groupI.parquet

print_test "Convert to CSV format"
${SCRIPT} convert ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    -f csv -o ${OUTPUT_DIR}/convert/groupI.csv

print_test "Convert to stdout (CSV)"
${SCRIPT} convert ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    -f csv -o stdout | head -20 > ${OUTPUT_DIR}/convert/groupI_head.csv

print_test "Convert with normalized column names"
${SCRIPT} convert ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --normalize -o ${OUTPUT_DIR}/convert/groupI_normalized.parquet

print_test "Convert with coordinate shifting (0-based to 1-based)"
${SCRIPT} convert ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --shift-start 1 -o ${OUTPUT_DIR}/convert/groupI_shifted.parquet

print_test "Convert multiple files using glob pattern"
${SCRIPT} convert "${GFF_DIR}/group*.gff" \
    -o ${OUTPUT_DIR}/convert/all_groups_glob.parquet

print_test "Convert with streaming mode (large files)"
${SCRIPT} convert ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --streaming -o ${OUTPUT_DIR}/convert/groupI_streaming.parquet

#==============================================================================
# MERGE COMMAND TESTS
#==============================================================================
echo -e "\n${YELLOW}=== MERGE COMMAND TESTS ===${NC}"

print_test "Merge multiple GFF files"
${SCRIPT} merge \
    ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    ${GFF_DIR}/groupII_GCA_031099375.1.gff \
    ${GFF_DIR}/groupIII_GCA_000880735.1.gff \
    -o ${OUTPUT_DIR}/merge/groups_I_II_III.parquet

print_test "Merge with glob pattern"
${SCRIPT} merge "${GFF_DIR}/groupI*.gff" "${GFF_DIR}/groupII*.gff" \
    -o ${OUTPUT_DIR}/merge/groups_I_and_II.parquet

print_test "Merge all files with normalization"
${SCRIPT} merge ${GFF_DIR}/*.gff \
    --normalize -o ${OUTPUT_DIR}/merge/all_normalized.parquet

print_test "Merge to CSV output"
${SCRIPT} merge ${GFF_DIR}/groupI*.gff ${GFF_DIR}/groupII*.gff \
    -f csv -o ${OUTPUT_DIR}/merge/merged.csv

print_test "Merge to stdout"
${SCRIPT} merge ${GFF_DIR}/groupI*.gff \
    -f csv -o stdout | head -30 > ${OUTPUT_DIR}/merge/merged_head.csv

#==============================================================================
# FILTER COMMAND TESTS
#==============================================================================
echo -e "\n${YELLOW}=== FILTER COMMAND TESTS ===${NC}"

print_test "Filter by feature type (CDS only)"
${SCRIPT} filter ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --type CDS -o ${OUTPUT_DIR}/filter/cds_only.csv

print_test "Filter by feature type (gene only)"
${SCRIPT} filter ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --type gene -o ${OUTPUT_DIR}/filter/genes_only.csv

print_test "Filter by minimum length"
${SCRIPT} filter ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --type CDS --min-length 500 -o ${OUTPUT_DIR}/filter/long_cds.csv

print_test "Filter by maximum length"
${SCRIPT} filter ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --type CDS --max-length 300 -o ${OUTPUT_DIR}/filter/short_cds.csv

print_test "Filter by length range"
${SCRIPT} filter ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --type CDS --min-length 300 --max-length 1000 \
    -o ${OUTPUT_DIR}/filter/medium_cds.csv

print_test "Filter by strand (positive strand)"
${SCRIPT} filter ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --strand + -o ${OUTPUT_DIR}/filter/plus_strand.csv

print_test "Filter by strand (negative strand)"
${SCRIPT} filter ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --strand - -o ${OUTPUT_DIR}/filter/minus_strand.csv

print_test "Filter by sequence ID (if applicable)"
# Get first seqid from file
FIRST_SEQID=$(${SCRIPT} print ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --head 1 --columns seqid -f csv 2>/dev/null | tail -1)
if [ ! -z "$FIRST_SEQID" ]; then
    ${SCRIPT} filter ${GFF_DIR}/groupI_GCA_000859985.2.gff \
        --seqid ${FIRST_SEQID} -o ${OUTPUT_DIR}/filter/single_seqid.csv
fi

print_test "Combined filters (CDS, long, positive strand)"
${SCRIPT} filter ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --type CDS --min-length 500 --strand + \
    -o ${OUTPUT_DIR}/filter/combined_filters.csv

print_test "Filter to GFF format"
${SCRIPT} filter ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --type gene -f gff -o ${OUTPUT_DIR}/filter/genes_only.gff

print_test "Filter to stdout"
${SCRIPT} filter ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --type CDS -o stdout | head -20 > ${OUTPUT_DIR}/filter/cds_head.csv

#==============================================================================
# SPLIT COMMAND TESTS
#==============================================================================
echo -e "\n${YELLOW}=== SPLIT COMMAND TESTS ===${NC}"

print_test "Split by feature type"
${SCRIPT} split ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --column type -d ${OUTPUT_DIR}/split/by_type/

print_test "Split by source"
${SCRIPT} split ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --column source -d ${OUTPUT_DIR}/split/by_source/

print_test "Split by strand"
${SCRIPT} split ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --column strand -d ${OUTPUT_DIR}/split/by_strand/

print_test "Split by seqid"
${SCRIPT} split ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --column seqid -d ${OUTPUT_DIR}/split/by_seqid/

print_test "Split to CSV format"
${SCRIPT} split ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --column type -d ${OUTPUT_DIR}/split/by_type_csv/ -f csv

print_test "Split to GFF format"
${SCRIPT} split ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --column type -d ${OUTPUT_DIR}/split/by_type_gff/ -f gff

#==============================================================================
# PRINT COMMAND TESTS
#==============================================================================
echo -e "\n${YELLOW}=== PRINT COMMAND TESTS ===${NC}"

print_test "Print first 10 rows (table format)"
${SCRIPT} print ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --head 10 > ${OUTPUT_DIR}/print/head10_table.txt

print_test "Print last 10 rows"
${SCRIPT} print ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --tail 10 > ${OUTPUT_DIR}/print/tail10_table.txt

print_test "Print specific columns"
${SCRIPT} print ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --columns seqid,type,start,end,strand --head 20 \
    > ${OUTPUT_DIR}/print/selected_columns.txt

print_test "Print with statistics"
${SCRIPT} print ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --stats > ${OUTPUT_DIR}/print/with_stats.txt

print_test "Print as CSV"
${SCRIPT} print ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    -f csv --head 20 > ${OUTPUT_DIR}/print/head20.csv

print_test "Print as JSON"
${SCRIPT} print ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    -f json --head 5 > ${OUTPUT_DIR}/print/head5.json

print_test "Print filtered by type with stats"
${SCRIPT} print ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --type CDS --stats > ${OUTPUT_DIR}/print/cds_stats.txt

print_test "Print filtered by length"
${SCRIPT} print ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --type CDS --min-length 1000 \
    > ${OUTPUT_DIR}/print/long_cds.txt

print_test "Print filtered by strand"
${SCRIPT} print ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    --strand + --head 20 > ${OUTPUT_DIR}/print/plus_strand.txt

#==============================================================================
# EXTRACT COMMAND TESTS
#==============================================================================
echo -e "\n${YELLOW}=== EXTRACT COMMAND TESTS ===${NC}"

print_test "Extract CDS sequences (nucleotide)"
${SCRIPT} extract \
    ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    ${FASTA_DIR}/groupI_GCA_000859985.2.fna \
    --type CDS -o ${OUTPUT_DIR}/extract/cds_nucleotide.fasta

print_test "Extract and translate CDS to proteins (genetic code 11)"
${SCRIPT} extract \
    ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    ${FASTA_DIR}/groupI_GCA_000859985.2.fna \
    --type CDS --outaa amino --genetic-code 11 \
    -o ${OUTPUT_DIR}/extract/cds_proteins.fasta

print_test "Extract genes (nucleotide)"
${SCRIPT} extract \
    ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    ${FASTA_DIR}/groupI_GCA_000859985.2.fna \
    --type gene -o ${OUTPUT_DIR}/extract/genes.fasta

print_test "Extract with minimum length filter"
${SCRIPT} extract \
    ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    ${FASTA_DIR}/groupI_GCA_000859985.2.fna \
    --type CDS --min-length 500 --outaa amino \
    -o ${OUTPUT_DIR}/extract/long_proteins.fasta

print_test "Extract from positive strand only"
${SCRIPT} extract \
    ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    ${FASTA_DIR}/groupI_GCA_000859985.2.fna \
    --type CDS --strand + \
    -o ${OUTPUT_DIR}/extract/plus_strand_cds.fasta

print_test "Extract with custom FASTA headers"
${SCRIPT} extract \
    ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    ${FASTA_DIR}/groupI_GCA_000859985.2.fna \
    --type CDS --id-columns seqid start end strand \
    -o ${OUTPUT_DIR}/extract/custom_headers.fasta

print_test "Extract to CSV format"
${SCRIPT} extract \
    ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    ${FASTA_DIR}/groupI_GCA_000859985.2.fna \
    --type CDS -f csv -o ${OUTPUT_DIR}/extract/cds_sequences.csv

print_test "Extract to Parquet format"
${SCRIPT} extract \
    ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    ${FASTA_DIR}/groupI_GCA_000859985.2.fna \
    --type CDS -f parquet -o ${OUTPUT_DIR}/extract/cds_sequences.parquet

print_test "Extract with name filter (if 'kinase' exists)"
${SCRIPT} extract \
    ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    ${FASTA_DIR}/groupI_GCA_000859985.2.fna \
    --name-contains "gene" \
    -o ${OUTPUT_DIR}/extract/name_filtered.fasta 2>/dev/null || echo "  (No matches found - normal)"

print_test "Extract from multiple FASTA files"
${SCRIPT} extract \
    ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    ${FASTA_DIR}/groupI_GCA_000859985.2.fna \
    ${FASTA_DIR}/groupII_GCA_031099375.1.fna \
    --type CDS -o ${OUTPUT_DIR}/extract/multi_fasta.fasta 2>/dev/null || echo "  (Expected: no matching seqids)"

print_test "Extract to stdout"
${SCRIPT} extract \
    ${GFF_DIR}/groupI_GCA_000859985.2.gff \
    ${FASTA_DIR}/groupI_GCA_000859985.2.fna \
    --type