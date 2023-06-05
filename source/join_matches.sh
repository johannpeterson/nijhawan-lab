#!/bin/zsh

csvtk join --left-join -t --fields "seq_fwd_1;seq_fwd_1" -  matchfile_fwd.tsv | \
csvtk join --left-join -t --fields "seq_rev_1;seq_rev_1" - matchfile_rev.tsv | \
csvtk join --left-join -t --fields "seq_fwd_rc_1;seq_fwd_rc_1" - matchfile_fwd_rc.tsv | \
csvtk join --left-join -t --fields "seq_rev_rc_1;seq_rev_rc_1" - matchfile_rev_rc.tsv
# csvtk filter2 -t -f 'len($barcode) < 32 && len($barcode_rc) < 32' < temp.4.tsv
