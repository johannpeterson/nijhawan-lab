#! /bin/bash
set -e

if [[ -f .env ]]; then
    export $(cat .env | xargs)
fi

while getopts ":d:s:" opt; do
    case ${opt} in
        d )
            DATA_DIR=$OPTARG
            ;;
        s )
            SOURCE_DIR=$OPTARG
            ;;
        \? )
            echo "Usage: start_notebook [-s sourcedir] [-d datadir]"
             ;;
        : )
            echo "$OPTARG requires an argument." 1>&2
            ;;
    esac
done

if [[ -z "${DATA_DIR}" ]]; then
    echo "Data directory must be specified with the DATA_DIR environment variable or with -d option."
    exit 1
fi

if [[ -z "${SOURCE_DIR}" ]]; then
    echo "Source directory must be specified with the SOURCE_DIR environment variable or with -s option."
    exit 1
fi

docker run \
       -p 8888:8888 \
       --volume=$SOURCE_DIR:/home/bio/source \
       --volume=$DATA_DIR:/data \
       -it nijhawanlab/tools:0.1
