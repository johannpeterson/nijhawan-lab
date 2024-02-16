#!/bin/zsh
csvtk cut -t -f fwd_primer,rev_primer,barcode \
	| csvtk sort -t -k fwd_primer,rev_primer,barcode \
	| csvtk freq -t -f 1,2,3 \
	| csvtk cut -t -f 1,2,4,3 \
	| csvtk sort -t -k 1,2 -k 3:nr
