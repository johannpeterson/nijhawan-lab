#!/bin/bash
PREFIX=VK003
time awk -F'\t' -vOFS='\n' '{print ">"$1, $2}' barcode.sequence.txt > barcode.fasta
time bwa index barcode.fasta
time bwa mem -t 8 -T 19 -Y barcode.fasta "$PREFIX"_R1_001.fastq.gz "$PREFIX"_R2_001.fastq.gz | gzip > "$PREFIX".barcode.sam.gz
time perl barcodes.count.pl "$PREFIX.barcode.sam.gz" | sed -r -n 's/^F_([^,]*),R_([^,]*)\t/\1\t\2\t/p' > "$PREFIX.barcode_pair.count.txt"
time perl barcode_pair_sequence.count.pl "$PREFIX.barcode.sam.gz" > "$PREFIX.barcode_pair_sequence.count.txt"
