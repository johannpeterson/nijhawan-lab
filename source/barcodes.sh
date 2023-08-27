#!/bin/zsh

SOURCEDIR=~/bio/nijhawanlab/source
MERGED_READS=$1
PRIMERS=primers.txt
PATTERNS=patterns.py
BARCODE_PATTERNS=barcode_patterns.py
MATCHES=matches.tsv
BARCODE_TABLE=barcode_table.tsv
BARCODE_COUNTS=barcode_counts.tsv

echo "get_regexes.sh"
echo "separate_matchtable.awk"
$SOURCEDIR/get_regexes.py $PRIMERS --patterns $PATTERNS | $SOURCEDIR/separate_matchtable.awk

echo "count_regex.py"
$SOURCEDIR/count_regex.py -s $MERGED_READS -p $PATTERNS -p $BARCODE_PATTERNS -s --out $MATCHES

echo "join_matches.sh | merge_names.awk"
$SOURCEDIR/join_matches.sh < $MATCHES | \
    $SOURCEDIR/merge_names.awk -v FILTER=1 > $BARCODE_TABLE

echo "Compute barcode counts"
$SOURCEDIR/count_barcodes.sh < $BARCODE_TABLE > $BARCODE_COUNTS
