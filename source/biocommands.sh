# sequence transformations
cdna() {tr "AaCcGgTt" "TtGgCcAa" <&0 >&1}
rcdna() {rev | tr "AaCcGgTt" "TtGgCcAa" <&0 >&1}

# generate shell variables for the sequences in a primer file
# file should have 3 columns: 1=label, 2=forward primer sequence, 3=reverse primer sequence
setseqvars() {$(awk '{print "export f"$1"="$2} {print "export r"$1"="$3}' $1)}

# pairgrep() {
#   pr --sep-string=' | ' -m -T -W 80 <(grep --color=always -e '$' -e $1 $2) <(grep --color=always -e '$' -e $1 $3) |less
# }

# Display corresponding reads side by side, with search sequence highlighted.
# e.g. pairgrep ACGT R1.fastq R2.fastq
pairgrep() {
    pr --sep-string=' | ' -m -T -W $COLUMNS $2 $3 |grep --color=always -e '$' -e $1 |less
}

# remove spaces & tabs preceding the end of line
# convert each series of spaces & tabs to a single tab
# Not clear why this doesn't work: sed -E 's/[ \t]+$//' -E 's/[ \t]+/\t/g' $1
cleantsv() {
    sed -E 's/[ \t]+$//' $1 | sed -E 's/[ \t]+/\t/g'
}

# Write one line for every pair of lines in file1, file2
allpairs() {
    while IFS= read -r line1; do
        while IFS= read -r line2; do
            echo $line1 '\t' $line2
        done < "$2"
    done < "$1"
}

# for paired primer file with fields: tag1, seq1, tag2, seq2,
# write a list of pairs as: tag1-tag2, seq1, seq2
# e.g., allpairs f_primers.tsv r_primers.tsv | allpairs
pairprimers() {
    allpairs $1 $2 | cleantsv | awk 'BEGIN{OFS="\t";} {print $1"-"$3,$2,$4}'
}

# highlight primers in different colors
# assumes the presence of four files containing the forward, reverse, reverse compliment forward & reverse primer sequences,
# as produced by `split_primers`
# e.g. phighlight seqeunces_R1.fastq
phighlight () {
    seqkit -w 0 fq2fa $1 | \
    GREP_COLOR='31;40' grep --colour=always -e '$' -f forward.txt | \
    GREP_COLOR='30;41' grep --colour=always -e '$' -f rcforward.txt | \
    GREP_COLOR='32;40' grep --colour=always -e '$' -f reverse.txt | \
    GREP_COLOR='30;42' grep --colour=always -e '$' -f rcreverse.txt | \
    less
}

phighlight_barcodes() {
    REF_PRE="TTCTTGACGAGTTCTTCTGA"
    REF_POST="ACGCGTCTGGAACAATCAAC"
    seqkit -w 0 fq2fa $1 | \
    GREP_COLOR='31;40' grep --colour=always -e '$' -f forward.txt | \
    GREP_COLOR='30;41' grep --colour=always -e '$' -f rcforward.txt | \
    GREP_COLOR='32;40' grep --colour=always -e '$' -f reverse.txt | \
    GREP_COLOR='30;42' grep --colour=always -e '$' -f rcreverse.txt | \
    GREP_COLOR='33;40' grep --colour=always -e '$' -e $REF_PRE | \
    GREP_COLOR='30;43' grep --colour=always -e '$' -e $REF_POST | \
    GREP_COLOR='30;106' grep --colour=always -E '([GC][AT]){9,}[GC]?|$' | \
    less
}

# extract sequences for forward & reverse primers from primers.txt or similarly formatted stream
# e.g., rprimers < primers.txt
rprimers() {awk '$4 ~ /R/ {print $2}' <&0 >&1}
fprimers() {awk '$4 ~ /F/ {print $2}' <&0 >&1}
rcrprimers() {rprimers <&0 | rcdna}
rcfprimers() {fprimers <&0 | rcdna}

# extract four sets of sequences from the primers.txt file, for forward, reverse, and reverse compliment of each
# first argument should be the name of the primers file `primers.txt`
# e.g. split_primers primers.txt
split_primers() {
    cat $1 | rprimers > reverse.txt
    cat $1 | fprimers > forward.txt
    cat $1 | rcrprimers > rcreverse.txt
    cat $1 | rcfprimers > rcforward.txt
}
