#!/bin/bash

for oldfile in `ls *.sra`
do
    echo $oldfile
    accession=${oldfile%.sra}
    newfile=$accession.bam
    if [[ ! -f newfile ]]
    then
        echo $accession $newfile
        sam-dump $accession | samtools view -bS - > $newfile
    fi
done;
    
