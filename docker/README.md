# Docker for picatrix

Picatrix has support for Docker. This is a convenient way of getting up and running.

### Install Docker
Follow the official instructions [here](https://www.docker.com/community-edition)

### Install Docker Compose
Follow the official instructions [here](https://docs.docker.com/compose/install/)

### Clone Picatrix

```shell
$ git clone https://github.com/google/picatrix.git
cd picatrix/docker
```

### Build and Start Containers

```shell
$ sudo docker-compose --env-file config.env up -d
```

To build the container use:

```shell
$ sudo docker-compose --env-file config.env build
```

### Access Picatrix

To access picatrix you need to find the token URL.

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

And make a copy of the URL that starts with `http://127.0....`

You can paste this URL into a browser and you should have a working Jupyter
installation with picatrix ready.

### Can I get Access to Data?

The /tmp/ folder is mounted as data inside the notebook container. Therefore if
you need to import data from your local machine, make a copy of it available in
the /tmp/ folder and read it from there (or change the docker config files to
expose other folders).
