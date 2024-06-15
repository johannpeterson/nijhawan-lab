#!/usr/bin/sed -En -f
#
# Generate two FASTA files of primer sequences from the single
# primers.txt table.
#
# ./primer_fasta.sed primers.txt --> forward.fasta & reverse.fasta

/^F/s/^(F[[:digit:]]+)[[:blank:]]+([[:alnum:]]+)[[:blank:]].+$/>\1\n\2/w forward.fasta
/^R/s/^(R[[:digit:]]+)[[:blank:]]+([[:alnum:]]+)[[:blank:]].+$/>\1\n\2/w reverse.fasta
