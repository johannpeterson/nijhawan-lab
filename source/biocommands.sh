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

allpairs() {
    while IFS= read -r line1; do
        while IFS= read -r line2; do
            echo $line1 '\t' $line2
        done < "$2"
    done < "$1"
}

pairprimers() {
    allpairs $1 $2 | cleantsv | awk 'BEGIN{OFS="\t";} {print $1"-"$3,$2,$4}'
}
