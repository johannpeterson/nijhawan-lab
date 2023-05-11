#!/bin/zsh
echo "Length of argument: "${#1}
for f in $@
do
    echo $f
done

files=*.fastq
echo "files: " $~files

echo $1
echo $~1
echo $^~1
echo "$~1"
echo "$^~1"
echo ${~1}
echo ${1[@]}

for f in ${~1}
do
    echo $f
done


