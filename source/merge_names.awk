#! awk -f

# https://stackoverflow.com/questions/37529232/awk-extract-data-from-a-column-by-name-rather-than-position

BEGIN {
    FS=OFS="\t"
    excluded_fields["name_fwd"] = \
        excluded_fields["name_fwd_rc"] = \
        excluded_fields["name_rev"] = \
        excluded_fields["name_rev_rc"] = ""
    filter = 0
}
FNR==1 {
    # print "Processing the 1st row."
    header_row="fwd_primer\trev_primer"
    for (i=1;i<=NF;i++) {
        fields[$i]=i
        if (!($i in excluded_fields))
            header_row=header_row"\t"$i
#        header_row = (header_row"\t"$i)
    }
    print header_row
    next
}
{
    fwd=rev=""
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
    if (!filter || fwd && rev) {
        row=fwd"\t"rev
        for (f in fields) {
            if (!(f in excluded_fields))
                row = row"\t"$(fields[f])
        }
        print row
    }
    next
}
