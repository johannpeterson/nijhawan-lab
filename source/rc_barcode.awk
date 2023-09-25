#! awk -f

# rc_barcode
# awk script to modify a TSV file by changing a single field ('barcode')
# to its reverse complement (in the DNA sense)

function reverse_complement(sequence)
{
    retval = ""
    for(i=length(sequence); i>0; i--) {
        l = substr(sequence, i, 1)
        c = (l=="A") ? "T" : (l=="T") ? "A" : (l=="G") ? "C" : (l=="C") ? "G" : l
        retval = retval c
    }
    return retval
}

BEGIN {
    FS=OFS="\t"
}

FNR==1 {
    for (i=1;i<=NF;i++) {
        fields[$i]=i
    }
    print
    next
}

{
    $(fields["barcode"]) = reverse_complement($(fields["barcode"]))
    print;
}
