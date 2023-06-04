#!/bin/zsh

csvtk join --left-join -t --fields "seq_fwd_1;seq_fwd_1" $1 matchfile_fwd.tsv > temp.1.tsv
csvtk join --left-join -t --fields "seq_rev_1;seq_rev_1" temp.1.tsv matchfile_rev.tsv > temp.2.tsv
csvtk join --left-join -t --fields "seq_fwd_rc_1;seq_fwd_rc_1" temp.2.tsv matchfile_fwd_rc.tsv > temp.3.tsv
csvtk join --left-join -t --fields "seq_rev_rc_1;seq_rev_rc_1" temp.3.tsv matchfile_rev_rc.tsv > temp.4.tsv
# csvtk filter2 -t -f 'len($barcode) < 32 && len($barcode_rc) < 32' < temp.4.tsv
