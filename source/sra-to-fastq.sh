#!/bin/bash
for sra_file in *.sra
do
    echo $sra_file
    time fastq-dump $sra_file
    # time fastq-dump $sra_file -Z | head -10
    echo
done
