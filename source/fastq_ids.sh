#!/bin/zsh
# 1       2   3                    4 5    6    7    8
# @A01940:313:GW2310153605th.Miseq:1:2101:1904:1251 1:N:0:ATCTCAGG+AGGCTTAG
# @Instrument:RunID:FlowCellID:Lane:Tile:X:Y ReadNum:FilterFlag:0:SampleNumber

echo "instrument\trunid\tflowcellid\tlane\ttile\tx\ty\tremainingfields"
# sed -E -n 's/^@([^:]+):([^:]+):([^:]+):([^:]+):([^:]+):([^:]+):([^\s]+)[[:space:]]+(.*$)/1=\1\t2=\2\t3=\3\t4=\4\t5=\5\t6=\6\t7=\7\t8=\8/p' $1
sed -E -n 's/^@([^:]+):([^:]+):([^:]+):([^:]+):([^:]+):([^:]+):([^\s]+)[[:space:]]+(.*$)/\1\t\2\t\3\t\4\t\5\t\6\t\7\t\8/p' $1
