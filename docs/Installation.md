# Installation

Picatrix can be installed via two ways:

1. docker
2. pip inside a virtualenv

Let's explore both methods:

## Docker

The easiest way to install picatrix is via docker. To use it, first
[install docker](https://docs.docker.com/engine/install/).

To run the docker container use:

```shell
$ git clone https://github.com/google/picatrix.git
$ cd picatrix/docker
```

*(if you don't have the git client installed you can also download
the [source code using this link](https://github.com/google/picatrix/archive/main.zip))*

By default the /tmp folder on your host will be mapped into a `data` folder
on the docker container. If you want to change that and point to another
folder on your system, edit the file `docker-latest.yml` and change the
path `/tmp` to a folder of your choosing (just remember that the folder needs to
be writable by `any` if you are running a Linux based host).

For instance if you are running this on a Windows system, then you will
need to change the `/tmp/` to something like `C:\My Folder\Where I store`.
Also when running on Windows, there is no `sudo` in front of the commands.

You also need to install `docker-compose`, please follow the instructions
[here](https://docs.docker.com/compose/install/) (the version that is often
included in your source repo might be too old to properly setup the container).

After that, just run:

```shell
$ sudo docker-compose -f docker-latest.yml --env-file config.env up -d
```

That will download the latest build and deploy the picatrix docker container.
To be able to connect to picatrix in a jupyter shell, run:

```shell
$ sudo docker logs docker_picatrix_1
...
    To access the notebook, open this file in a browser:
        file:///home/picatrix/.local/share/jupyter/runtime/nbserver-6-open.html
    Or copy and paste one of these URLs:
        http://....:8899/?token=...
     or http://127.0.0.1:8899/?token=...
...
```

On Windows you can also use the Docker Desktop client and click the running
Docker container to get the log window open and copy the URL from there.

Copy the URL that starts with `http://127.0.0.....` and paste it into a browser
window and you should have a fully working copy of Jupyter running, with an
active picatrix library.

Also remember that all notebooks you create inside the container that are
not part of the `data` folder, that is that are created inside the container
itself will be deleted once the container is upgraded. It is therefore
recommended to create all notebooks that you wish to store inside the `data`
folder of the container (which is mapped to a folder on the host).

### Upgrade Container

To upgrade the container using the latest build, you can run:

```shell
$ sudo docker pull us-docker.pkg.dev/osdfir-registry/picatrix/picatrix:latest
```

After updating the image the container needs to be recreated

*warning: all notebooks that are stored inside the container, that is not
in the `data` folder in the docker container will be lost once these
commands are executed. If you want the notebooks to survive, make sure
that the notebooks are stored on the host (which means to store them in
the data folder in the container, which is mapped to a directory on the
host itself).*

```shell
$ sudo docker stop docker_picatrix_1
$ sudo docker rm docker_picatrix_1
$ cd picatrix/docker
$ sudo docker-compose -f docker-latest.yml --env-file config.env up -d
```

## Virtualenv

To install picatrix using virtualenv you can use the following commands:

```shell
$ python3 -m venv picatrix_env
$ source picatrix_env/bin/activate
$ pip install picatrix
```

And then to start picatrix you can either run:

```shell
$ jupyter notebook
```

If you want to connect from a colab frontend, then you'll need to run these
two commands as well:

```shell
$ pip install jupyter_http_over_ws
$ jupyter serverextension enable --py jupyter_http_over_ws
```

And then to run the notebook:

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

*(that is convert the IP address 127.0.0.1 to the domain name localhost)*

Then select the arrow next to the `Connect` button, select `Connect to local
runtime` and type in the URL with the token value into the `Backend URL`
field and hit `CONNECT`.
