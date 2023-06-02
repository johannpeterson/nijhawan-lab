#! awk -f

# https://stackoverflow.com/questions/37529232/awk-extract-data-from-a-column-by-name-rather-than-position

BEGIN { FS=OFS="\t" }
FNR==1 { for (i=1;i<=NF;i++) fields[$i]=i; next }
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
    print $(fields["name_fwd"]),$(fields["name_fwd_rc"]),$(fields["name_rev"]),$(fields["name_rev_rc"]),fwd,rev
}
