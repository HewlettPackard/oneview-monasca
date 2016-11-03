# -*- encoding: utf-8 -*-
#
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


class Default:
    def __init__(self):
        self.retry_interval = '2'
        self.auth_retry_limit = '2'
        self.debug = 'true'


class ConfOneview:
    def __init__(self):
        self.host = '127.0.0.1'
        self.username = 'admin'
        self.password = 'password'


class ConfServerList:
    def __init__(self, mac_file):
        self.mac_file_path = mac_file


class Conf:
    def __init__(self, mac_file_path=None):
        self.DEFAULT = Default()
        self.oneview = ConfOneview()
        self.serverlist = ConfServerList(mac_file_path)
