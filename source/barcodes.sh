SOURCEDIR=~/bio/nijhawanlab/source
echo "get_regexes.sh"
$SOURCEDIR/get_regexes.py primers.txt --patterns patterns.py | $SOURCEDIR/separate_matchtable.awk
echo "separate_matchtable.awk"
#$SOURCEDIR/separate_matchtable.awk
echo "count_regex.py"
$SOURCEDIR/count_regex.py -s VK003_bbmerge.fastq -p patterns.py -p barcode_patterns.py -s --out matches.tsv
echo "join_matches.sh | merge_names.awk"
$SOURCEDIR/join_matches.sh < matches.tsv | \
    $SOURCEDIR/merge_names.awk -v FILTER=1 > barcode_table.tsv
