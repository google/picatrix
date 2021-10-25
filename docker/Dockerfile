FROM python:3.8-slim

# Create folders and fix permissions.
RUN groupadd --gid 1000 picagroup && \
    useradd picatrix --uid 1000 --gid 1000 -d /home/picatrix -m && \
    mkdir -p /usr/local/src/picadata/ && \
    chmod 777 /usr/local/src/picadata/

USER picatrix
WORKDIR /home/picatrix
ENV VIRTUAL_ENV=/home/picatrix/picenv

RUN python3 -m venv $VIRTUAL_ENV && \
    mkdir -p .ipython/profile_default/startup/ && \
    mkdir -p /home/picatrix/.jupyter

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV JUPYTER_PORT=8899

COPY --chown=1000:1000 docker/notebook_init.py /home/picatrix/.ipython/profile_default/startup/notebook_init.py
COPY --chown=1000:1000 . /home/picatrix/code
COPY --chown=1000:1000 docker/jupyter_notebook_config.py /home/picatrix/.jupyter/jupyter_notebook_config.py

RUN pip install --upgrade pip setuptools wheel && \
    cd /home/picatrix/code && pip install -e .[runtime] && \
    bash prepare-picatrix-runtime.sh

WORKDIR /usr/local/src/picadata/
EXPOSE 8899

# Run jupyter.
ENTRYPOINT ["jupyter", "notebook"]
