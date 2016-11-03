#!/usr/bin/env bash
# (c) Copyright 2016 Hewlett Packard Enterprise Development LP
# Copyright 2016 Universidade Federal de Campina Grande
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

set -x

BASE_DIR=$(pwd)

function install_python(){

  # Installs Python 2.7.9 on Ubuntu 14.04 to include security updates
  # Run this script with superuser privileges.
  #
  # Make sure only root can run our script
  if [ "$(id -u)" != "0" ]; then
     echo "This script must be run as root" 1>&2
     exit 1
  fi

  BASEDEPS="build-essential python-pip python-dev"
  BUILDDEPS="libbz2-dev \
  libc6-dev \
  libgdbm-dev \
  libncursesw5-dev \
  libreadline-gplv2-dev \
  libsqlite3-dev \
  libssl-dev \
  tk-dev"

  TARFILE="Python-2.7.9.tgz"
  TARHOST="https://www.python.org/ftp/python/2.7.9"
  SRCDIR="Python-2.7.9"

  apt-get update
  apt-get install -y $BASEDEPS $BUILDDEPS

  if [ ! -e $SRCDIR ]; then
  	wget "$TARHOST/$TARFILE"
  	tar xvf $TARFILE
  fi

  cd $SRCDIR
  ./configure
  make
  make install

  cd ..
  python -m ensurepip --upgrade

  echo "removing source files"
  rm $TARFILE
  rm -r $SRCDIR
  cd $BASE_DIR
}


install_python
set +x
