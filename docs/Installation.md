# Installation

Picatrix can be installed via two ways:

1. docker
2. pip inside a virtualenv

Let's explore both methods:

## Docker

The easiest way to install picatrix is via docker. To use it, first
[install docker](https://docs.docker.com/engine/install/). You may also want to
make sure you can run docker [sudo-less](https://docs.docker.com/engine/install/linux-postinstall/).

To run the docker container use:

```shell
$ git clone https://github.com/google/picatrix.git
$ cd picatrix/docker
$ sudo docker-compose -f docker-latest.yml --env-file config.env up -d
```

That will download the latest build and deploy the picatrix docker container.
To be able to connect to picatrix in a jupyter shell, run:

```shell
$ CONTAINER_ID=`sudo docker container list | grep docker_picatrix | awk '{print $1}'`
$ sudo docker logs $CONTAINER_ID
...
    To access the notebook, open this file in a browser:
        file:///home/picatrix/.local/share/jupyter/runtime/nbserver-6-open.html
    Or copy and paste one of these URLs:
        http://....:8899/?token=...
     or http://127.0.0.1:8899/?token=...
...
```

Copy the URL that starts with `http://127.0.0.....` and paste it into a browser
window and you should have a fully working copy of Jupyter running, with an
active picatrix library.


## Virtualenv

To install picatrix using virtualenv you can use the following commands:

```shell
$ python3 -m venv picatrix_env
$ source picatrix_env/bin/activate
$ pip install picatrix
$ pip install jupyter_http_over_ws
$ jupyter serverextension enable --py jupyter_http_over_ws
```

And then to start picatrix you can either run:

```shell
$ jupyter notebook
```

Or if you want to connect from a colab frontend:

```shell
$ jupyter notebook \
  --NotebookApp.allow_origin='https://colab.research.google.com' \
  --port=8888 \
  --NotebookApp.port_retries=0
```

## Confirm Installation

You can confirm the successful installation by creating a new notebook and type in:
```
%picatrixmagics
```

Picatrix library is already imported and initialized.

## Connect To Colab

In order to use the docker container for colab, you may need to change the URL
that was provided from:

`http://127.0.0.1:8899/?token=...` to `http://localhost:8899/?token=...`.

Then select the arrow next to the `Connect` button, select `Connect to local
runtime` and type in the URL with the token value into the `Backend URL`
field and hit `CONNECT`.
