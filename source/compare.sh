#!/bin/zsh

FASTQ_FILE="/Users/johann/Google Drive/My Drive/nijhawanlab/amplicons/VK003new/aligned/VK003new_merged.fastq"
COUNTS_FILE="/Users/johann/Google Drive/My Drive/nijhawanlab/amplicons/VK003new/old_analysis/VK003new_top_10_reads.tsv"

SOURCE_DIR="/Users/johann/bio/nijhawanlab/source"

F_PRIMER=$1
R_PRIMER=$2

TEMP_FILE=$(mktemp)
trap 'rm -f "$TEMP_FILE"' EXIT

$SOURCE_DIR/extract-barcodes.sh $1 $2 "$FASTQ_FILE" > "$TEMP_FILE"

$SOURCE_DIR/compare_barcodes.py -1 $COUNTS_FILE \
                                -2 $TEMP_FILE \
                                -f $1 -r $2 \
    |csvtk -t head|csvtk -t pretty
