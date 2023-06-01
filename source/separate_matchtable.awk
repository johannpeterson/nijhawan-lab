#! awk -f
FILE_FWD="matchfile_fwd.tsv"
FILE_REV="matchfile_rev.tsv"
FILE_FWD_RC="matchfile_fwd_rc.tsv"
FILE_REV_RC="matchfile_rev_rc.tsv"

BEGIN {
    FS="\t"
    OFS="\t"
    print "name_fwd","seq_fwd_1" > "matchfile_fwd.tsv"
    print "name_rev","seq_rev_1" > "matchfile_rev.tsv"
    print "name_fwd_rc","seq_fwd_rc_1" > "matchfile_fwd_rc.tsv"
    print "name_rev_rc","seq_rev_rc_1" > "matchfile_rev_rc.tsv"
    
}
{if ($2=="SEQ_FWD") print $1"\t"$3 > FILE_FWD}
{if ($2=="SEQ_REV") print $1"\t"$4 > FILE_REV}
{if ($2=="SEQ_FWD_RC") print $1"\t"$5 > FILE_FWD_RC}
{if ($2=="SEQ_REV_RC") print $1"\t"$6 > FILE_REV_RC}
