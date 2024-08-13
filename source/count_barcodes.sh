#!/bin/zsh

# usage: count_barcodes.sh fwd_primer_seq rev_primer_seq merged_reads.fastq
#  -> barcodes.txt & counts.txt
#
# Generates a list of all barcodes for the given primers,
# and a table of their counts.
#
# The 1st and 2nd arguments are the forward and reverse primer sequences.
# The third argument is the name of the FASTA or FASTQ file with
# the merged reads.  These environment variables must be defined:
#
# SEQ_PRE
# SEQ_POST
# SEQ_PRERC
# SEQ_POSTRC
#
# which define the flanking sequence before and after the barcode.

rcdna() {rev | tr "AaCcGgTt" "TtGgCcAa" <&0 >&1}

F=$1
R=$2
Frc=`echo $F|rcdna`
Rrc=`echo $R|rcdna`
SED1="s|^.*${SEQ_PRE}\(.*\)${SEQ_POST}.*$|\1|p"
SED2="s|^.*${SEQ_POSTRC}\(.*\)${SEQ_PRERC}.*$|\1|p"

echo "F=$F" >&2
echo "R=$R" >&2
echo "Frc=$Frc" >&2
echo "Rrc=$Rrc" >&2
echo "SEQ_PRE=$SEQ_PRE" >&2
echo "SEQ_POST=$SEQ_POST" >&2
echo "SEQ_PRERC=$SEQ_PRERC" >&2
echo "SEQ_POSTRC=$SEQ_POSTRC" >&2
echo "search file: $3" >&2
echo "SED1=$SED1" >&2
echo "SED2=$SED2" >&2

grep --color=never "$F" "$3" | \
    grep --color=never "$Rrc" | \
    sed -n -e "$SED1" > barcodes.txt

grep --color=never "$R" "$3" | \
    grep --color=never "$Frc" | \
    sed -n -e "$SED2" | \
    rcdna >> barcodes.txt

sort barcodes.txt | uniq -c | sort -nr > counts.txt
