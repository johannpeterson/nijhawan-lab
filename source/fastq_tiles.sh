#!/bin/zsh

fastq_ids.sh $1 | csvtk -t summary -g tile -f x:min,x:max,y:min,y:max
