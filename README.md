# nijhawan-lab
Files for [UTSW Nijhawan lab](https://www.utsouthwestern.edu/labs/nijhawan/) bioinformatics analyses.

This reposity contains files required to build a Docker image containing GATK, Jupyter notebook and other tools used in bioinformatics analyses.

## Installation
To use this Docker image:
1. Install Docker
1. Create or navigate to your data directory:

        cd /home/me/biodata
        
1. Test Docker:

        docker --version
        
1. Pull the Docker image:

        docker pull nijhawanlab/tools:latest

1. You can now run the image:

        docker run -it --entrypoint "bash" nijhawanlab/tools
        root@5ce12013aeae:/usr/bin#
        
But to make it useful, you will need the image to have access to your local directory.  Use the `docker run -v` option:

        docker run -it --entrypoint "bash" -v /local/dir:/containers/dir nijhawanlab/tools
        
