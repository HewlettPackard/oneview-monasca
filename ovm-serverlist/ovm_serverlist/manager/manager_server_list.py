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

"""
Manages the HLM Component.
"""

from ovm_serverlist.model.node import Node
from ovm_serverlist.model.metric import Metric
from ovm_serverlist.shared import utils as utils
from ovm_serverlist.shared import log as logging
from ovm_serverlist.shared import constants as const
from ovm_serverlist.manager.abstract_manager_server_list import AbstractManagerServerList

import yaml

LOG = logging.get_logger(__name__)


class ManagerServerList(AbstractManagerServerList):
    """
    The HLM Manager.
    """
    def __init__(self, mac_file_path, manager_oneview, debug=False):
        """ ManagerHLM constructor.
        :param mac_file_path:
        :param manager_oneview:
        """
        super(ManagerServerList, self).__init__()
        utils.print_log_message('Info', 'Initialize ServerList Manager', LOG)

        self.__mac_file_path = mac_file_path
        self.__manager_oneview = manager_oneview
        self.__debug = debug
        self.__servers = []

    def load_mac_file(self):
        """ Load a list of dicts. Each dict have two keys: 'mac-adrr' that will
        be used to get a server_hardware_uuid and 'dimensions' for the new
        metric.
        """
        try:
            with open(self.__mac_file_path, 'r') as mac_file:
                mac_file_loaded = yaml.safe_load(mac_file)
                if mac_file_loaded:
                    servers = mac_file_loaded['servers']
                else:
                    servers = []

                mac_file.close()
                utils.print_log_message('Debug', 'Reading successful mac file', LOG, self.__debug)
                self.__servers = servers
        except IOError as ex:
            utils.print_log_message('Error', 'Error reading the mac file: %s.' % ex, LOG)
            raise

    def get_nodes_associated_oneview(self):
        """Get a set of Nodes of server hardware associated to HLM services.

        :rtype: A :set:`set <Nodes>`
        :returns the collection of associated nodes.
        """
        message = 'Initialize get_nodes_associated_oneview method'
        utils.print_log_message('Info', message, LOG)
        nodes = set()

        for mac in self.__servers:
            server_hardware_uuid = self.__manager_oneview.get_server_hardware_uuid(mac['mac-addr'])
            if server_hardware_uuid:
                dimensions = {str(k): str(v) for k, v in mac['dimensions'].items()}
                dimensions['server_hardware_uuid'] = server_hardware_uuid

                metrics = set()
                metrics.add(Metric(const.METRIC_NAME, dimensions))
                nodes.add(Node(server_hardware_uuid, metrics))

        return nodes
