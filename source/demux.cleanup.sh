#!/bin/zsh
# re: constructing an array from lines in a file:
# https://unix.stackexchange.com/questions/29724/how-to-properly-collect-an-array-of-lines-in-zsh

array_of_lines=("${(@f)$(cut --fields=1 --delimiter=' ' primers.tsv)}")

rm NB_R1_001_UNKNOWN.fastq
rm NB_R2_001_UNKNOWN.fastq
for primer in $array_of_lines
do
    files=(
        "R1_$primer.fastq"
        "R2_$primer.fastq"
        "NB_R1_001_$primer.fastq"
        "NB_R2_001_$primer.fastq"
        "NB_R1_001_$primer.paired.fastq"
        "NB_R2_001_$primer.paired.fastq"
    )
    echo $primer
    for f in $files; do
        echo $f
        if [[ -f $f ]] then
           rm $f
        fi
    done
done
