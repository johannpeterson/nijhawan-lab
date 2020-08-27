# docker build -t $DOCKER_IMAGE .

# Docker image for Nijhawan Lab, UTSW
# Contains:
#   GATK
#   samtools
#   sra-toolkit
#   NCBI datasets utility
#   Jupyter Notebooks

# Notes:
# - Running Jupyter in a Docker container:
#     https://github.com/ReproNim/neurodocker/issues/82
# TODO:
# - resolve persmission & user issues
# - get a better .profile with aliases, etc.
# - install NCBI SRA toolkit - done?
# - and NCBI datasets tool - done?
# - problems setting up sra-toolkit in Docker image:
#     https://github.com/ncbi/sra-tools/issues/291
#     https://hub.docker.com/r/ncbi/sra-tools

FROM broadinstitute/gatk:4.1.8.1
ARG VERSION=0.2
LABEL version=$VERSION
LABEL description="Tools for bioinformatics used by Nijhawan Lab, UTSW"

ENV BIO_USER      bio
ENV BIO_GROUP     bio
ENV HOME_DIR      /home/bio
ENV JUPYTER_PORT  8888
ENV DATA_DIR      $HOME_DIR/data
ENV SOURCE_DIR    $HOME_DIR/source

ENTRYPOINT ["jupyter", "notebook", "--allow-root", "--ip=0.0.0.0", "--no-browser"]

# The recommended way to install packages:
# RUN apt-get update && apt-get install -y \
#   packagename \
#   && rm -rf /var/lib/apt/lists/*

# SRA-Toolkit doesn't seem to be installing
RUN apt-get update && apt-get --quiet install -y \
    sra-toolkit \
    samtools \
    time uuid-runtime curl \
    && rm -rf /var/lib/apt/lists/*

# OR:
# other libraries needed to build samtools:
#   zlib1g-dev libncurses5-dev libncursesw5-dev libbz2-dev liblzma-dev \
# Here:
# - download samtools source
# - ./configure
# - make
# - make install

COPY requirements.txt /home/bio/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /home/bio/requirements.txt

# install NCBI datasets utility
WORKDIR /usr/bin
RUN ["curl", "-o", "datasets", "https://ftp.ncbi.nlm.nih.gov/pub/datasets/command-line/LATEST/linux-amd64/datasets"]
RUN ["chmod", "+x", "datasets"]

# Jupyter notebook server port
EXPOSE $JUPYTER_PORT

RUN groupadd $BIO_GROUP && \
    useradd --create-home --home-dir $HOME_DIR \
    --gid $BIO_USER \
    --groups sudo \
    $BIO_GROUP

RUN mkdir $DATA_DIR && mkdir $SOURCE_DIR
VOLUME $DATA_DIR $SOURCE_DIR

COPY docker/jupyter_notebook_config.py /root/.jupyter/
# COPY provenance.sh /usr/local/bin/provenance

# USER $BIO_USER
# WORKDIR $HOME_DIR
