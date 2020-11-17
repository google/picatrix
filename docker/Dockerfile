FROM python:3.8-slim

# Create folders and fix permissions.
RUN groupadd --gid 1000 picagroup && \
    useradd picatrix --uid 1000 --gid 1000 -d /home/picatrix -m && \
    mkdir -p /usr/local/src/picadata/notebooks && \
    chmod 777 /usr/local/src/picadata/ && \
    chmod 777 /usr/local/src/picadata/notebooks && \
    find /usr/local/src/picadata/notebooks -type d -exec chmod 777 {} \; && \
    find /usr/local/src/picadata/notebooks -type f -exec chmod 644 {} \; 

USER picatrix
WORKDIR /home/picatrix
RUN mkdir -p .ipython/profile_default/startup/

USER root
COPY docker/00-import.py /home/picatrix/.ipython/profile_default/startup/00-import.py
RUN chown picatrix /home/picatrix/.ipython/profile_default/startup/00-import.py
USER picatrix

ENV VIRTUAL_ENV=/home/picatrix/picenv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --chown=1000:1000 . /home/picatrix/code
RUN pip install --upgrade pip setuptools wheel && \
    cd /home/picatrix/code && pip install -e . && \
    pip install --upgrade jupyter_http_over_ws && \
    jupyter serverextension enable --py jupyter_http_over_ws

WORKDIR /usr/local/src/picadata/
ENV JUPYTER_PORT=${JUPYTER_PORT}
EXPOSE ${JUPYTER_PORT}

# Run jupyter.
CMD jupyter notebook --port ${JUPYTER_PORT} \ 
    --NotebookApp.allow_origin='https://colab.research.google.com' \ 
    --NotebookApp.port_retries=0 --ip '*'
