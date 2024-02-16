#! awk -f

# merge_names
# awk script to choose forward or reverse-complement primers & barcodes
# Expects a TSV file with fileds name_fwd, name_fwd_rc, name_rev, name_rev_rc,
# barcode_fwd, barcode_rc.  The output will contain fields barcode, fwd_primer & rev_primer.
# FILTER, if set, excludes lines without both forward & reverse primers and without a barcode.
# BC_LENGTH, if set, adds a column containing the length of the barcode string.
#
# e.g. merge_names.awk -v FILTER=1 -v BC_LENGTH=1 temp.4.tsv

# For awk advice on the header row:
# https://stackoverflow.com/questions/37529232/awk-extract-data-from-a-column-by-name-rather-than-position

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
    excluded_fields["name_fwd"] = \
        excluded_fields["name_fwd_rc"] = \
        excluded_fields["name_rev"] = \
        excluded_fields["name_rev_rc"] = \
        excluded_fields["seq_fwd_1"] = \
        excluded_fields["seq_fwd_rc_1"] = \
        excluded_fields["seq_rev_1"] = \
        excluded_fields["seq_rev_rc_1"] = \
        ""
}

FNR==1 {
    for (i=1;i<=NF;i++) {
        fields[$i]=i
    }
    header_row="fwd_primer\trev_primer\tbarcode\trc"
    if (BC_LENGTH) header_row = header_row"\tbarcode_length"
    for (f in fields) {
        if (!(f in excluded_fields))
            header_row = header_row"\t"$(fields[f])
    }
    print header_row
    next
}

{
    fwd=rev=barcode=rc=""
    if ($(fields["name_fwd"]) && !$(fields["name_fwd_rc"])) {
        fwd=$(fields["name_fwd"])
        # print "name_fwd"
    }
    else if ($(fields["name_fwd_rc"]) && !$(fields["name_fwd"])) {
        # print "name_fwd_rc"
        fwd=$(fields["name_fwd_rc"])
    }
    if ($(fields["name_rev"]) && !$(fields["name_rev_rc"])) {
        rev=$(fields["name_rev"])
        # print "name_fwd"
    }
    else if ($(fields["name_rev_rc"]) && !$(fields["name_rev"])) {
        # print "name_fwd_rc"
        rev=$(fields["name_rev_rc"])
    }
    if ($(fields["barcode_fwd"]) && !$(fields["barcode_rc"])) {
        barcode = $(fields["barcode_fwd"])
        rc = 0
        # print "name_fwd"
    }
    else if ($(fields["barcode_rc"]) && !$(fields["barcode_fwd"])) {
        # print "name_fwd_rc"
        barcode = reverse_complement($(fields["barcode_rc"]))
        rc = 1
    }
    if (!FILTER || (fwd && rev && barcode)) {
        row=fwd"\t"rev"\t"barcode"\t"rc
        if (BC_LENGTH) {row = row"\t"length(barcode)}
        for (f in fields) {
            if (!(f in excluded_fields))
                row = row"\t"$(fields[f])
        }
        print row
    }
    next
}
