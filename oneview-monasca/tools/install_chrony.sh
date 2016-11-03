#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: ./install_chrony.sh <ntp-server>"
    exit 1
fi

sudo apt-get install chrony -y
sudo sed -e '0,/^server.*/s//server '"$1"' iburst/; /server [[:digit:]]\+\.debian/ s/^#*/#/' -i /etc/chrony/chrony.conf
sudo service chrony restart
