# sequence transformations
cdna() {tr "AaCcGgTt" "TtGgCcAa" <&0 >&1}
rcdna() {rev | tr "AaCcGgTt" "TtGgCcAa" <&0 >&1}

# generate shell variables for the sequences in a primer file
# file should have 3 columns: 1=label, 2=forward primer sequence, 3=reverse primer sequence
setseqvars() {$(awk '{print "export f"$1"="$2} {print "export r"$1"="$3}' $1)}

# pairgrep() {
#   pr --sep-string=' | ' -m -T -W 80 <(grep --color=always -e '$' -e $1 $2) <(grep --color=always -e '$' -e $1 $3) |less
# }

pairgrep() {
    pr --sep-string=' | ' -m -T -W $COLUMNS $2 $3 |grep --color=always -e '$' -e $1 |less
}
