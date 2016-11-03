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
Manages the Ironic Component
"""

from ironicclient.common.apiclient.exceptions import AuthorizationFailure
from ovm_ironic.manager.abstract_manager_ironic import AbstractManagerIronic
from ovm_ironic.shared.exceptions import LoginFailException
from ovm_ironic.shared import constants as const
from ovm_ironic.shared import log as logging
from ovm_ironic.shared import utils as utils
from ovm_ironic.model.metric import Metric
from ironicclient import client as ironic
from ovm_ironic.model.node import Node

LOG = logging.get_logger(__name__)


class ManagerIronic(AbstractManagerIronic):
    """
    The Ironic Manager.
    """
    def __init__(self, username, password, auth_url, tenant_name, api_version, insecure,
                 max_attempt=0, debug=False):
        super(ManagerIronic, self).__init__()
        utils.print_log_message('Info', 'Initializing Ironic Manager...', LOG)

        self.__debug = debug
        self.__username = username
        self.__password = password
        self.__auth_url = auth_url
        self.__tenant_name = tenant_name
        self.__insecure = insecure
        self.__api_version = api_version
        self.__max_attempt = int(max_attempt)

    def _get_ironic_client(self):
        """Provides an Ironic client according a configuration file

        :returns: the Ironic client.
        """
        kwargs = {
            'os_username': self.__username,
            'os_password': self.__password,
            'os_auth_url': self.__auth_url,
            'os_tenant_name': self.__tenant_name,
            'os_ironic_api_version': self.__api_version
        }

        if self.__insecure.lower() == 'true':
            kwargs['insecure'] = True

        message = "Using OpenStack credentials specified in the configuration" \
                  + " file to get Ironic Client"
        utils.print_log_message('Debug', message, LOG, self.__debug)

        return ironic.get_client(const.API_VERSION, **kwargs)

    def _get_node_list(self):
        """Gets a collection of nodes of the ironic client.

        :returns the collection of nodes.
        """
        try:
            client = self._get_ironic_client()
            return client.node.list(detail=True)
        except AuthorizationFailure as ex:
            utils.print_log_message('Error', ex.message)
            raise LoginFailException("Cannot authorize connect to ironic API client.")
        except:
            raise

    def get_node_list(self):
        """Call the function get_node_list encapsulate into try_execute function
        """
        return utils.try_execute(self._get_node_list, self.__max_attempt, 2000)

    def get_nodes_associated_oneview(self, ironic_nodes):
        """Gets a set of Nodes of server hardware associated to HLM services.

        :param ironic_nodes: a collection of nodes.
        :rtype: A :set:`set <Nodes>`
        :returns the collection of associated nodes.
        """
        interest_nodes = set()
        utils.print_log_message(
            'Debug', "Getting associated nodes from Ironic...", LOG, self.__debug)
        for node in ironic_nodes:
            if node.driver in const.SUPPORTED_DRIVERS:
                oneview_uri = node.driver_info['server_hardware_uri']
                server_hardware_uuid = utils.extract_oneview_uuid(oneview_uri)

                dimensions = const.TEMPLATE_DIMENSIONS
                dimensions['server_hardware_uuid'] = server_hardware_uuid
                dimensions['service'] = const.SERVICE_NAME
                dimensions['resource_id'] = utils.extract_ironic_uuid(node)

                metrics = set()
                metrics.add(Metric(const.METRIC_NAME, dimensions))
                interest_nodes.add(Node(server_hardware_uuid, metrics))

        return interest_nodes
