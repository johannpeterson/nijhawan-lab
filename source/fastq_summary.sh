#!/bin/zsh
fastq_ids.sh $1 | csvtk -t summary \
                        -f instrument:unique,runid:unique,flowcellid:unique,lane:unique,tile:countunique \
                | csvtk -t pretty
