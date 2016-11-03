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

""" This module contains the classes needed to get a fake config file
to be used into the tests.
"""

import os


class Conf:
    """ Principal class of the module. It contains objects with
    the configuration of each section present into real conf file.
    """
    def __init__(self):
        """ Class constructor.
        Instantiate each fake section.
        """
        self.DEFAULT = Default()
        self.hlm = ConfHLM()
        self.oneview = ConfOneview()
        self.openstack = ConfOpenstack()
        self.ironic = ConfIronic()
        self.tooz = ConfTooz()


class Default:
    """ This class represents the fake section DEFAULT of fake conf file.
    """
    def __init__(self):
        """ Fake section constructor.
        """
        self.retry_interval = '100'
        self.auth_retry_limit = '5'
        self.periodic_refresh_interval = '2'
        self.batch_publishing_interval = '150'
        self.scmb_certificate_dir = os.path.expanduser('~')


class ConfHLM:
    """ This class represents the fake section ConfHLMn of the fake conf file.
    """
    def __init__(self, macs='00:00:00:00:00:00'):
        """ Fake section constructor.
        """
        self.macs = macs
        self.mac_file_path = './mac-file.yaml'


class ConfOneview:
    """ This class represents the fake section ConfOneview of the fake conf file.
    """
    def __init__(self):
        """ Fake section constructor.
        """
        self.host = '127.0.0.1'
        self.manager_url = 'https://127.0.0.1/'
        self.username = 'user'
        self.password = 'password'
        self.max_attempt = 1


class ConfOpenstack:
    """ This class represents the fake section ConfOpenstack of the fake conf file.
    """
    def __init__(self):
        """ Fake section constructor
        """
        self.auth_url = 'http://127.0.0.1:5000/v3'
        self.auth_user = 'user'
        self.auth_password = 'password'
        self.auth_tenant_name = 'project'
        self.monasca_api_version = '2_0'


class ConfIronic:
    """ This class represents the fake section Ironic of the fake conf file.
    """
    def __init__(self):
        """ Fake section constructor
        """
        self.auth_url = 'http://127.0.0.1:5000/v2.0/'
        self.admin_user = 'user'
        self.admin_password = 'password'
        self.admin_tenant_name = 'project'
        self.insecure = 'false'
        self.ironic_api_version = '1.11'


class ConfTooz:
    """ This class represents the fake section Tooz of the fake conf file.
    """
    def __init__(self):
        self.coordinator_url = 'kazoo://127.0.0.1:2181'
        self.group_name = 'oneview_group'
