#!/bin/zsh

pattern_file='/Users/johann/bio/nijhawanlab/source/sequences.sh'

declare -A pattern_lookup
for name value in `awk -F= '{print $1,$2}' $pattern_file`
do
    pattern_lookup[$name]=$value
done

for file in $@
do
    for key val in ${(@fkv)pattern_lookup}
    do
        echo "$file\t$key\t$val\t"$(grep --count -E ${val} ${1})
     done
done
