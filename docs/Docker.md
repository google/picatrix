# Docker

Picatrix can be run as a docker image. To use it, first
[install docker](https://docs.docker.com/engine/install/). You may also want to
make sure you can run docker [sudo-less](https://docs.docker.com/engine/install/linux-postinstall/).

To get picatrix up and running on docker (from source files):

```shell
$ git clone https://github.com/google/picatrix.git
$ cd picatrix/docker
$ sudo docker-compose --env-file config.env up -d
```

That will build and deploy the picatrix docker container. To be able to connect
to picatrix in a jupyter shell, run:

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

You can confirm that by creating a new notebook and type in:
```
%picatrixmagics`
```

Picatrix library is already imported and initialized.

## Connect To Colab

In order to use the docker container for colab, you may need to change the URL
that was provided from:

`http://127.0.0.1:8899/?token=...` to `http://localhost:8899/?token=...`.

Then select the arrow next to the `Connect` button, select `Connect to local
runtime` and type in the URL with the token value into the `Backend URL`
field and hit `CONNECT`.

## Rebuild

If you make changes to the dockerfiles please run:

```shell
sudo docker-compose --env-file config.env build
```

Before:

```shell
$ sudo docker-compose --env-file config.env up -d
```
