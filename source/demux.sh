#!/bin/zsh

# Script to demultiplex paired-end FASTQ files based on a list of primers.
# Input:
#   primers.tsv - 1st column is the primer/group name, second column is the sequence of the primer/barcode
#   r1_file.fastq & r2_file.fastq

# dependencies:
#   seqkit
#   demultiplex
#   datamash
#   zsh, cut, tr

# Variables you need to change:
R1All="NB_R1_001"
R2All="NB_R2_001"
PrimerFile="primers.3.tsv"

primer_list=("${(@f)$(cut --fields=1 $PrimerFile)}")
echo $primer_list

R1ReadsFile="$R1All.fastq"
R2ReadsFile="$R2All.fastq"

# Separately demultiplex the R1 reads file and the R2 reads file:
echo $R1ReadsFile $R2ReadsFile
demultiplex match primers.tsv NB_R1_001.fastq
demultiplex match primers.tsv NB_R2_001.fastq

# For each primer/group in the primers.tsv file,
# pair the R1 reads matching that group with the corresponding
# reads from the original R2 file, and pair the R2 reads matching
# the group with the corresponding reads from the original R1
# file.  Append both R1 & R2 files together.
for primer in $primer_list
do
        R1File=$R1All"_"$primer
        R2File=$R2All"_"$primer
        R1Out="R1_"$primer".fastq"
        R2Out="R2_"$primer".fastq"
        echo $primer '\t' $R1File '\t' $R2File '\t' $R1Out '\t' $R2Out

        seqkit pair -1 $R1File".fastq" -2 $R2All".fastq"
        seqkit pair -1 $R1All".fastq" -2 $R2File".fastq"

        mv $R1File".paired.fastq" $R1Out
        mv $R2All".paired.fastq" $R2Out

        cat $R1All".paired.fastq" >> $R1Out
        cat $R2File".paired.fastq" >> $R2Out

        rm $R1All".paired.fastq" $R2File".paired.fastq"
done

seqkit stats $R1ReadsFile $R2ReadsFile
echo "R1_BC?.fastq: " $(seqkit stats R1_BC?.fastq |tr -d ','|datamash --header-in -W sum 4)
echo "R1_BC?.fastq: " $(seqkit stats R1_BC?.fastq |tr -d ','|datamash --header-in -W sum 4)
