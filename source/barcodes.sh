#!/bin/zsh

SOURCEDIR=~/bio/nijhawanlab/source

# Required input files:
MERGED_READS=$1
BARCODE_PATTERNS=barcode_patterns.py
PRIMERS=primers.txt
SAMPLES=samples.tsv

# Intermediate and result files:
PATTERNS=patterns.py
MATCHES=matches.tsv
BARCODE_TABLE=barcode_table.tsv
BARCODE_COUNTS=barcode_counts.tsv
BARCODE_COUNTS_SAMPLES=barcode_counts_samples.tsv
FLAT_SAMPLES=flat_samples.tsv
COUNTS=totals_by_sample.tsv

echo "get_regexes.py"
echo "separate_matchtable.awk"
$SOURCEDIR/get_regexes.py $PRIMERS --patterns $PATTERNS | $SOURCEDIR/separate_matchtable.awk

echo "count_regex.py"
$SOURCEDIR/count_regex.py -s $MERGED_READS -p $PATTERNS -p $BARCODE_PATTERNS -s --out $MATCHES

echo "join_matches.sh | merge_names.awk"
$SOURCEDIR/join_matches.sh < $MATCHES | \
    $SOURCEDIR/merge_names.awk -v FILTER=1 > $BARCODE_TABLE

echo "Compute barcode counts"
$SOURCEDIR/count_barcodes.sh < $BARCODE_TABLE > $BARCODE_COUNTS

echo "Flatten samples table"
$SOURCEDIR/flatten_samples.py $SAMPLES $FLAT_SAMPLES

echo "Join with sample names"
csvtk join -t --left-join -f "fwd_primer,rev_primer" $BARCODE_COUNTS $FLAT_SAMPLES > $BARCODE_COUNTS_SAMPLES

echo "Compute totals for each sample."
csvtk summary -t -g sample,fwd_primer,rev_primer -f frequency:sum $BARCODE_COUNTS_SAMPLES > $COUNTS
