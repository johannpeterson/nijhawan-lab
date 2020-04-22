# docker build -t nijhawanlab/tools:0.1 .

FROM broadinstitute/gatk:4.1.6.0

ENV BIO_USER      bio
ENV BIO_GROUP     bio
ENV HOME_DIR      /home/bio
ENV JUPYTER_PORT  8888
ENV DATA_DIR      $HOME_DIR/data
ENV SOURCE_DIR    $HOME_DIR/source

# Running Jupyter in a Docker container:
# https://github.com/ReproNim/neurodocker/issues/82

# TODO:
# - resolve persmission & user issues
# - get a better .profile...

ENTRYPOINT ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser"]

# RUN apt-get update && apt-get install -y \
#   packagename \
#   && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install notebook

# Jupyter notebook server port
EXPOSE $JUPYTER_PORT

# Are these flags right?
RUN groupadd $BIO_GROUP && useradd --create-home --home-dir $HOME_DIR -g $BIO_USER $BIO_GROUP

RUN mkdir $DATA_DIR && mkdir $SOURCE_DIR
VOLUME $DATA_DIR $SOURCE_DIR

USER $BIO_USER
WORKDIR $HOME_DIR
