#! awk -f
BEGIN { FS=OFS="\t" }
FNR==1 { for (i=1;i<=NF;i++) fields[$i]=i; next }
{
    fwd=""
    if ($(fields["name_fwd"]) && !$(fields["name_fwd_rc"])) {
        fwd=$(fields["name_fwd"])
        # print "name_fwd"
    }
    else if ($(fields["name_fwd_rc"]) && !$(fields["name_fwd"])) {
        # print "name_fwd_rc"
        fwd=$(fields["name_fwd_rc"])
    }
    print $(fields["name_fwd"]),$(fields["name_fwd_rc"]),fwd
}

