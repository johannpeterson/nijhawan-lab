#! awk -f

BEGIN {
    if (! FILE_FWD) {
        FILE_FWD="matchfile_fwd.tsv"
    }
    if (! FILE_REV) {
        FILE_REV="matchfile_rev.tsv"
    }
    if (! FILE_FWD_RC) {
        FILE_FWD_RC="matchfile_fwd_rc.tsv"
    }
    if (! FILE_REV_RC) {
        FILE_REV_RC="matchfile_rev_rc.tsv"
    }
    FS="\t"
    OFS="\t"
    print "name_fwd","seq_fwd_1" > FILE_FWD
    print "name_rev","seq_rev_1" > FILE_REV
    print "name_fwd_rc","seq_fwd_rc_1" > FILE_FWD_RC
    print "name_rev_rc","seq_rev_rc_1" > FILE_REV_RC
}
$2=="SEQ_FWD" {print $1"\t"$3 > FILE_FWD;}
$2=="SEQ_REV" {print $1"\t"$4 > FILE_REV;}
$2=="SEQ_FWD_RC" {print $1"\t"$5 > FILE_FWD_RC;}
$2=="SEQ_REV_RC" {print $1"\t"$6 > FILE_REV_RC;}
