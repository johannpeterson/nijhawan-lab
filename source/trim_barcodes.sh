#!/bin/zsh

csvtk cut -t -f fwd_primer,rev_primer,barcode < $1 \
    | csvtk -t filter2 -t -f 'len($barcode)<30' \
    | csvtk sort -t -k fwd_primer -k rev_primer -k barcode \
    | datamash -H -g fwd_primer,rev_primer,barcode count barcode \
    | csvtk rename2 -t -F -f "*" -p "GroupBy\((.*)\)" -r '$1' \
    | csvtk sort -t -k fwd_primer -k rev_primer -k 'count(barcode)':nr
