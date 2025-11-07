#!/bin/bash

# Bash script to download GFF and FASTA files for viruses
# of multiple Baltimore groups using NCBI Datasets command-line tool

# Define Baltimore groups (examples: dsDNA - group I; ssDNA - group II; dsRNA - group III, etc.)
# We'll use some representative viruses for several Baltimore groups as examples

# requires ncbi-datasets-cli (https://github.com/ncbi/datasets)
declare -A baltimore_examples_extended
baltimore_examples_extended=(
    ["I"]="GCA_000859985.2" #"Herpes simplex virus type 1"     # dsDNA viruses
    ["II"]="GCA_031099375.1" #"feline Parvovirus"   # ssDNA viruses
    ["III"]="GCA_000880735.1" #"Rotavirus A"              # dsRNA viruses
    ["IV"]="GCA_031102545.1"	 # "Poliovirus"                # (+)ssRNA viruses
    ["V"]="GCA_053294245.1"	 # "Influenza A virus"          # (−)ssRNA viruses 
    ["VI"]="GCA_000864765.1" #"Human immunodeficiency virus 1" # ssRNA-RT viruses
    ["VII"]="GCA_031171435.1" #"bat Hepadnavirus"             # dsDNA-RT viruses
    ["cirular_rna"]="GCA_050924405.1" #"Tulasnella ambivirus 3"             # circular RNA viruses
)


# Output directories
mkdir -p downloaded_gff downloaded_fasta

for group in "${!baltimore_examples_extended[@]}"; do
    virus="${baltimore_examples_extended[$group]}"
    outprefix="group${group// /_}_${virus// /_}"

    echo "Downloading data for Baltimore group $group: $virus"

    # Download GFF
    ./datasets download genome accession "$virus" --filename "${outprefix}_genome.zip" --include gff3,genome   #--exclude-atypical --assembly-source refseq  --fast-zip-validation
    unzip -o "${outprefix}_genome.zip" -d "tmp_${outprefix}"

    if [ -d "tmp_${outprefix}/ncbi_dataset/data" ]; then
        find "tmp_${outprefix}/ncbi_dataset/data" -name "*.gff" -exec cp {} "./downloaded_gff/${outprefix}.gff" \;
        find "tmp_${outprefix}/ncbi_dataset/data" -name "*.fna" -exec cp {} "./downloaded_fasta/${outprefix}.fna" \;
    fi

    rm -rf "tmp_${outprefix}" "${outprefix}_genome.zip"
done

echo "Download complete. GFF and FASTA files are in downloaded_gff/ and downloaded_fasta/."


