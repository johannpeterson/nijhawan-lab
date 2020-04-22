# docker build -t nijhawanlab/tools:0.1 .

# Running Jupyter in a Docker container:
# https://github.com/ReproNim/neurodocker/issues/82

# TODO:
# - resolve persmission & user issues
# - get a better .profile...
# Disable token auth for Jupyter:
#   c.NotebookApp.token = ''
#   c.NotebookApp.password = ''

FROM broadinstitute/gatk:4.1.6.0

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

RUN pip install --upgrade pip
RUN pip install notebook

# Jupyter notebook server port
EXPOSE $JUPYTER_PORT

RUN groupadd $BIO_GROUP && \
    useradd --create-home --home-dir $HOME_DIR \
    --gid $BIO_USER \
    --groups sudo \
    $BIO_GROUP

RUN mkdir $DATA_DIR && mkdir $SOURCE_DIR
VOLUME $DATA_DIR $SOURCE_DIR

COPY jupyter_notebook_config.py /root/.jupyter/
COPY provenance.sh /usr/local/bin/provenance

# USER $BIO_USER
# WORKDIR $HOME_DIR
