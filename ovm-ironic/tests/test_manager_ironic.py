# Copyright 2016 Hewlett Packard Enterprise Development LP
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

"""Unit test cases for the manager_ironic.py module.
"""

from base import TestBase
from tests.shared.config import ConfIronic
from tests.shared.fake import FakeNodeIronic

from ironicclient import exc
from ovm_ironic.shared import constants as const
from ironicclient.v1.client import Client as Ironic
from ovm_ironic.manager.manager_ironic import ManagerIronic

import mock


class TestManagerIronic(TestBase):
    """This class test the manager_ironic module from the
    ovm_ironic.manager.
    """
    def setUp(self):
        """Setting up the tests.
        """
        super(TestManagerIronic, self).setUp()
        conf = ConfIronic()

        self.manager = ManagerIronic(
            conf.admin_user,
            conf.admin_password,
            conf.auth_url,
            conf.admin_tenant_name,
            conf.ironic_api_version,
            conf.insecure,
            max_attempt='2'
        )

    def tearDown(self):
        """Tearing down the tests.
        """
        super(TestManagerIronic, self).tearDown()

    def test_manager_get_nodes_associated_oneview(self):
        """Test case regarding the get_nodes_associated_oneview method.
                >>> Create a collection of nodes based on the return of the method;
                >>> Checks if the collection length is 1; and,
                >>> For each node in the collection:
                >>>     Checks if the node name is not None;
                >>>     Checks if the node name is not empty; and,
                >>>     For each metric in the metrics collection of the node:
                >>>     Check if the service name is in the dimensions value.
        """
        ironic_nodes = FakeNodeIronic.fake_get_node_list()
        nodes = self.manager.get_nodes_associated_oneview(ironic_nodes)
        self.assertEquals(len(nodes), 1)
        for node in nodes:
            self.assertIsNotNone(node.server_hardware_uuid)
            self.assertNotEqual(node.server_hardware_uuid, '')
            for metric in node.metrics:
                self.assertTrue(const.SERVICE_NAME in metric.dimensions.values())

    @mock.patch("ironicclient.v1.node.NodeManager.list")
    @mock.patch("keystoneauth1.session.Session.get_endpoint")
    def test_get_node_list(self, mock_get_endpoint, mock_node_list):

        raised = False
        ironic_nodes = FakeNodeIronic.fake_get_node_list()
        mock_get_endpoint.side_effect = exc.AmbigiousAuthSystem("Something happening")
        try:
            self.manager.get_node_list()
        except:
            raised = True

        self.assertTrue(raised)
        self.assertFalse(mock_node_list.called)

        mock_get_endpoint.side_effect = None
        mock_node_list.return_value = ironic_nodes
        mock_get_endpoint.return_value = 'http://127.0.0.1:35357/v2.0'

        raised, result = False, None
        try:
            result = self.manager.get_node_list()
        except:
            raised = True

        self.assertFalse(raised)
        self.assertEqual(result, ironic_nodes)
        self.assertTrue(mock_node_list.called)

    @mock.patch("keystoneauth1.session.Session.get_endpoint")
    def test_get_ironic_client(self, mock_get_endpoint):
        mock_get_endpoint.return_value = 'http://127.0.0.1:35357/v2.0'
        client = self.manager._get_ironic_client()

        self.assertTrue(mock_get_endpoint.called)
        self.assertIsInstance(client, Ironic)
