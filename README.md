# nijhawanlab

Files for [UTSW Nijhawan lab](https://www.utsouthwestern.edu/labs/nijhawan/) bioinformatics analyses.

This reposity contains files required to build a Docker image containing GATK, Jupyter notebook and other tools used in bioinformatics analyses.

## Installation
### Install [Docker](https://www.docker.com/products/docker-desktop)
### Create or navigate to your data directory

        cd /home/me/biodata

### Test Docker

        docker --version
        
### Pull the Docker image

        docker pull nijhawanlab/tools:latest

### Start a container with the image

        docker run -it --entrypoint "bash" nijhawanlab/tools
        
You should get the command prompt for the container:

        root@5ce12013aeae:/usr/bin#
        
To make it useful, you will need to give the image access to your local directory.  Use the `docker run -v` option:

        docker run -it --entrypoint "bash" -v $(pwd):/data nijhawanlab/tools
        
This is facilitated by the `start_here.sh` script, which you can download from [here](https://github.com/johannpeterson/nijhawanlab/blob/master/start_here.sh?raw=true).  The entire contents is as follows.

        #!/bin/bash
        docker run \
                --entrypoint "bash" \
                --volume $(pwd):/data \
                --workdir "/data" \
                -it nijhawanlab/tools:latest
