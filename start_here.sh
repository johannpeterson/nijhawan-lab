#!/bin/bash
docker run \
       --entrypoint "bash" \
       --volume $(pwd):/data \
       --workdir "/data" \
       -it nijhawanlab/tools:latest
