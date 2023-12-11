#!/bin/zsh
# extract-barcodes.sh
#
# Shell script to pull barcodes for a specific pair of primers from a single FASTQ/FASTA file.
# e.g. extract-barcodes.sh oVK810 oVK790 my.fastq

rcdna() {rev | tr "AaCcGgTt" "TtGgCcAa" <&0 >&1}

# Figure out the primer sequences to search for.
# This asusmes pre-defined variables for each primer sequence and its reverse complement,
# e.g., oVK790=ACTGACTGACTGACTG,...
# Indirection in zsh uses ${(P)varname}.  In bash would be ${!varname} (I think)
BC1=${(P)1}
BC2=${(P)2}
BC1RC_NAME="$1rc"
BC2RC_NAME="$2rc"
BC1RC=${(P)BC1RC_NAME}
BC2RC=${(P)BC2RC_NAME}
echo $1"="$BC1 >&2
echo $BC1RC_NAME"="$BC1RC >&2
echo $2"="$BC2 >&2
echo $BC2RC_NAME"="$BC2RC >&2

# create temporary names pipes and set trap to delete them on exit
FWDFILE=$(uuidgen).temp
REVFILE=$(uuidgen).temp
TEMPFILE=$(uuidgen).temp
mkfifo $FWDFILE $REVFILE $TEMPFILE
trap 'rm -f "$TEMPFILE" "$FWDFILE" "$REVFILE"' EXIT

# pull only sequences with the correct forward & reverse primers:
grep $BC1RC < $3 | grep $BC2 | tee $FWDFILE > $REVFILE &
grep $BC1 < $3 | grep $BC2RC | tee $FWDFILE > $REVFILE &

# extract barcodes:
echo "barcode" > $TEMPFILE &
sed -n -E 's/.*TTCTTGACGAGTTCTTCTGA(.+)ACGCGTCTGGAACAATCAAC.*/\1/p' $FWDFILE >> $TEMPFILE &
sed -n -E 's/.*GTTGATTGTTCCAGACGCGT(.+)TCAGAAGAACTCGTCAAGAA.*/\1/p' $REVFILE | rcdna >> $TEMPFILE &

# group & count barcodes
echo "barcode\tcount(barcode)"
datamash --sort --header-in groupby barcode count barcode < $TEMPFILE | sort -nr -k 2

