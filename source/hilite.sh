#!/bin/zsh

usage() {
cat << EOF 
Usage: $0 [-f filename] [-h]
If a pattern file is not specified with -f, patterns should be stored in a file highlights in the current directory.

EOF
exit 1
}
 
normal='\x1b[0m'
bold='\x1b[1m'
COLORS=('\x1b[31m' '\x1b[32m' '\x1b[33m' '\x1b[34m' '\x1b[35m' '\x1b[36m') 

PATTERN_FILE=highlights
while getopts "hf:" o; do
    case "${o}" in
        f)
            PATTERN_FILE=${OPTARG}
            ;;
        h)
            usage
            ;;
        *)
            usage
            ;;
    esac
done

if [[ ! -f $PATTERN_FILE ]]; then
    echo "Pattern file $PATTERN_FILE not found."
    usage
fi

PATTERNS=()
while IFS='' read -r LINE || [ -n "${LINE}" ]; do
    echo "processing pattern: ${LINE}"
    PATTERNS+=${LINE}
done < $PATTERN_FILE

cmds=()
for ((i=1; i <= $#PATTERNS; i++ )) do
    cmd="s/${PATTERNS[i]}/${COLORS[i]}&$normal/g"
    echo $cmd
    cmds+=(-e "$cmd")
done

shift "$(($OPTIND -1))"
sed ${cmds[@]} $1
