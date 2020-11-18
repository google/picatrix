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
$ sudo docker-compose -f docker-build.yml build
$ sudo docker-compose -f docker-build.yml up -d
```

To build the container use:

```shell
$ sudo docker-compose --env-file config.env build
```

### Access Picatrix

To access picatrix you need to start a browser and paste in the following
URL: http://localhost:8899/?token=picatrix

And you should have a working Jupyter installation with picatrix ready.

If you want to change the token, edit the file `docker/jupyter_notebook_config.py`
before building the docker image.

### Can I get Access to Data?

The /tmp/ folder is mounted as data inside the notebook container. Therefore if
you need to import data from your local machine, make a copy of it available in
the /tmp/ folder and read it from there (or change the docker config files to
expose other folders).
