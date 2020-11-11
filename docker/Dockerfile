# Use the official Docker Hub Ubuntu 18.04 base image
FROM ubuntu:20.04

# Workaround for bug in setuptools v50.
# Ref: https://github.com/pypa/setuptools/issues/2350
ENV SETUPTOOLS_USE_DISTUTILS=stdlib
ENV JUPYTER_PORT=${JUPYTER_PORT}

# Prevent needing to configure debian packages, stopping the setup of
# the docker container.
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    python3-virtualenv \
    python3-venv \
    python3-pip \
    python3-wheel \
    python3-setuptools \
    python3-psycopg2 \
    git \
    wget \
  && rm -rf /var/lib/apt/lists/*

RUN echo 'debconf debconf/frontend select Dialog' | debconf-set-selections

# Create folders and fix permissions.
RUN useradd picatrix -d /home/picatrix -m
RUN mkdir -p /usr/local/src/picadata/notebooks
RUN chmod 777 /usr/local/src/picadata/
RUN chmod 777 /usr/local/src/picadata/notebooks
RUN find /usr/local/src/picadata/notebooks -type d -exec chmod 777 {} \;
RUN find /usr/local/src/picadata/notebooks -type f -exec chmod 644 {} \;

USER picatrix
WORKDIR /home/picatrix
# TODO: Enable this after fixing permission issues with the runtime file.
# RUN mkdir -p .local/share/jupyter/runtime/
RUN mkdir -p .ipython/profile_default/startup/

USER root
COPY docker/00-import.py /home/picatrix/.ipython/profile_default/startup/00-import.py
RUN chown picatrix /home/picatrix/.ipython/profile_default/startup/00-import.py
# TODO: Enable this after fixing permission issues with the runtime file.
# RUN chmod 777 /home/picatrix/.local/share/jupyter/runtime/
USER picatrix

ENV VIRTUAL_ENV=/home/picatrix/picenv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install picatrix.
RUN pip install wheel
RUN pip install --upgrade picatrix
RUN pip install jupyter_http_over_ws
RUN jupyter serverextension enable --py jupyter_http_over_ws

WORKDIR /usr/local/src/picadata/
EXPOSE ${JUPYTER_PORT}

# Run jupyter.
CMD jupyter notebook --port ${JUPYTER_PORT} \ 
	--NotebookApp.allow_origin='https://colab.research.google.com' \ 
	--NotebookApp.port_retries=0 --ip '*'
