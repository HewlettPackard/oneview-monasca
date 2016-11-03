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

function install_hponeview(){
  git clone https://github.com/HewlettPackard/python-hpOneView.git
  cd python-hpOneView
  pip install . --upgrade
  cd $BASE_DIR
  rm -rf python-hpOneView
}

install_hponeview
set +x
