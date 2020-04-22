#! /bin/bash
DATA_DIR='/Volumes/home/bio'
SOURCE_DIR=`pwd`
docker run \
       --entrypoint "bash" \
       --volume=$SOURCE_DIR:/home/bio/source \
       --volume=$DATA_DIR:/data \
       -it nijhawanlab/tools:0.1
