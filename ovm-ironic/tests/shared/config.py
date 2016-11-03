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


class ConfHLM:
    def __init__(self, macs='00:00:00:00:00:00'):
        self.macs = macs


class ConfOneview:
    def __init__(self):
        self.host = '127.0.0.1'
        self.userName = 'admin'
        self.password = 'password'


class ConfIronic:
    def __init__(self):
        self.auth_url = 'http://127.0.0.1:5000/v2.0/'
        self.admin_user = 'user'
        self.admin_password = 'password'
        self.admin_tenant_name = 'project'
        self.insecure = 'true'
        self.ironic_api_version = '1.11'


class Conf:
    def __init__(self):
        self.DEFAULT = Default()
        self.hlm = ConfHLM()
        self.oneview = ConfOneview()
        self.ironic = ConfIronic()
