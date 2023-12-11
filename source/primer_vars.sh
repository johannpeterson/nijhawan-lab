#!/bin/zsh
# primer_vars.sh < primers.txt
# OR
# eval "$(./primer_vars.sh < primers.txt)"
awk '{printf "export %s=%s\nexport %src=$(echo %s | rcdna)\n", $1, $2, $1, $2}'
