# Use the official Docker Hub Ubuntu 18.04 base image
#FROM ubuntu:20.04
FROM python:3.8-slim

# Prevent needing to configure debian packages, stopping the setup of
# the docker container.
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update && apt-get install -y --no-install-recommends git \
  && rm -rf /var/lib/apt/lists/*

# Create folders and fix permissions.
RUN useradd picatrix -d /home/picatrix -m && mkdir -p /usr/local/src/picadata/notebooks && \
    chmod 777 /usr/local/src/picadata/ && \
    chmod 777 /usr/local/src/picadata/notebooks && \
    find /usr/local/src/picadata/notebooks -type d -exec chmod 777 {} \; && \
    find /usr/local/src/picadata/notebooks -type f -exec chmod 644 {} \; 

USER picatrix
WORKDIR /home/picatrix
RUN mkdir -p .ipython/profile_default/startup/

USER root
#RUN pip install virtualenv
COPY docker/00-import.py /home/picatrix/.ipython/profile_default/startup/00-import.py
RUN chown picatrix /home/picatrix/.ipython/profile_default/startup/00-import.py
USER picatrix

ENV VIRTUAL_ENV=/home/picatrix/picenv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install picatrix.
RUN pip install --upgrade pip setuptools wheel && \
    pip install --upgrade picatrix jupyter_http_over_ws && \
    jupyter serverextension enable --py jupyter_http_over_ws

WORKDIR /usr/local/src/picadata/
ENV JUPYTER_PORT=${JUPYTER_PORT}
EXPOSE ${JUPYTER_PORT}

# Run jupyter.
CMD jupyter notebook --port ${JUPYTER_PORT} \ 
    --NotebookApp.allow_origin='https://colab.research.google.com' \ 
    --NotebookApp.port_retries=0 --ip '*'
