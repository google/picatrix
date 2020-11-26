#!/bin/bash
# This is a very simple installation script that will only
# work on Linux based systems.
# This will create a data folder and make sure the permissions
# are correct.

mkdir -p ${HOME}/picadata
cp -r notebooks ${HOME}/picadata/example_notebooks
sudo chgrp -R 1000 ${HOME}/picadata
find ${HOME}/picadata -type d -exec chmod 770 {} \;
find ${HOME}/picadata -type f -exec chmod 660 {} \;

cd docker
cat docker-compose.yml| sed -e 's/\/tmp\//~\/picadata/g' > docker-tmp.yml
sudo docker-compose -f docker-tmp.yml up -d
rm docker-tmp.yml
cd ..

echo "Open http://localhost:8899/?token=picatrix in a browser window."
