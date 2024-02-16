# docker build -t $DOCKER_IMAGE .

# Docker image for Nijhawan Lab, UTSW
# Contains:
#       csvtk
#       python

FROM ubuntu:latest
# continuumio/miniconda3
ARG VERSION=0.0.1
LABEL version=$VERSION
LABEL description="Tools for amplicon analysis used by Nijhawan Lab, UTSW"

ENV BIO_USER      bio
ENV BIO_GROUP     bio
ENV HOME_DIR      /home/bio
# ENV JUPYTER_PORT  8888
ENV DATA_DIR      $HOME_DIR/data
ENV SOURCE_DIR    $HOME_DIR/source

# required executables:
# csvtk
# flash2
# separate_matchtable.awk
# merge_names.awk
# count_barcodes.sh
# get_regexes.py
# count_regex.py
# flatten_samples.py
# barchart_grid.py

# argparse
# os
# sys
# csv
# types
# regex
# itertools
# Bio
# re
# email
# matplotlib
# seaborn
# pandas

# ENTRYPOINT ["jupyter", "notebook", "--allow-root", "--ip=0.0.0.0", "--no-browser"]

# The recommended way to install packages:
# RUN apt-get update && apt-get install -y \
#   packagename \
#   && rm -rf /var/lib/apt/lists/*

# RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update && apt upgrade -y && apt-get --quiet install -y \
    time uuid-runtime curl unzip make \
    build-essential zlib1g-dev \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# OR:
# other libraries needed to build samtools:
#   zlib1g-dev libncurses5-dev libncursesw5-dev libbz2-dev liblzma-dev \
# Here:
# - download samtools source
# - ./configure
# - make
# - make install

# COPY requirements.txt /home/bio/requirements.txt
# RUN pip install --upgrade pip
# RUN pip install -r /home/bio/requirements.txt
 
# install NCBI datasets utility
# WORKDIR /usr/bin
# RUN ["curl", "-o", "datasets", "https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/LATEST/linux-amd64/datasets"]
# RUN ["chmod", "+x", "datasets"]

# install seqkit
# https://bioinf.shenwei.me/seqkit/
# https://github.com/shenwei356/seqkit/releases/download/v0.14.0/seqkit_linux_amd64.tar.gz
# RUN ["curl", "-L", "-o", \
#     "seqkit.tar.gz", \
#     "https://github.com/shenwei356/seqkit/releases/download/v0.14.0/seqkit_linux_amd64.tar.gz"]
# RUN ["tar", "-xvf", "seqkit.tar.gz"]
# RUN ["wget", "https://github.com/shenwei356/seqkit/releases/download/v0.16.1/seqkit_linux_amd64.tar.gz"]
# RUN ["tar", "-xvf", "seqkit_linux_amd64.tar.gz"]

# Jupyter notebook server port
# EXPOSE $JUPYTER_PORT

# RUN conda create -n bio -c bioconda \
#     python=3.10
# RUN conda install -c bioconda flash2
# RUN conda install -c bioconda csvtk

# flash2
# https://github.com/dstreett/FLASH2/archive/refs/heads/master.zip
WORKDIR /usr/bin
RUN ["curl", "-L", "-o", \
    "flash2.zip", \
    "https://github.com/dstreett/FLASH2/archive/refs/heads/master.zip"]
RUN ["unzip", "-o", "flash2.zip"]
WORKDIR /usr/bin/FLASH2-master
RUN make
RUN cp ./flash2 /usr/bin/flash2

# csvtk
# https://github.com/shenwei356/csvtk/releases/download/v0.29.0/csvtk_linux_arm64.tar.gz
WORKDIR /usr/bin
RUN ["curl", "-L", "-o", \
    "csvtk_linux_arm64.tar.gz", \
    "https://github.com/shenwei356/csvtk/releases/download/v0.29.0/csvtk_linux_arm64.tar.gz"]
RUN ["tar", "-xvf", "csvtk_linux_arm64.tar.gz"]

RUN echo "Building for ${BUILDARCH}"

# RUN conda config --env --add channels bioconda

RUN groupadd $BIO_GROUP && \
    useradd --create-home --home-dir $HOME_DIR \
    --gid $BIO_USER \
    --groups sudo \
    $BIO_GROUP

RUN mkdir $DATA_DIR && mkdir $SOURCE_DIR
VOLUME $DATA_DIR $SOURCE_DIR

# USER $BIO_USER
# WORKDIR $HOME_DIR
