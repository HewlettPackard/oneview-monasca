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
Unit test cases for the ironic.py module.
"""

from time import sleep

from ovm_ironic.shared import utils
from stevedore.extension import Extension
from ovm_ironic.driver.ironic import DiscoveryNodeIronicProvider

from base import TestBase
from tests.shared.config import Conf
from tests.shared.fake import FakeNodeIronic
from tests.shared.fake import FakeComponentListener

import mock


class TestIronic(TestBase):
    """This class test the ironic module from the ovm_ironic.driver.
    """
    def setUp(self):
        super(TestIronic, self).setUp()

        self.alias = 'ovm_ironic'
        self.namespace = 'node_discovery.driver'

        self.conf = Conf()
        self.fake_listener = FakeComponentListener()

    def tearDown(self):
        super(TestIronic, self).tearDown()

    @mock.patch('stevedore.extension.ExtensionManager._load_plugins')
    def test_load_plugin(self, mock_driver):
        """Test case regarding the instance after calling the load_plugin method.
        Test flow:
                >>> Checks if the loaded plugin is an instance of DiscoveryNodeHLMProvider.
        """
        mock_driver.return_value = [
            Extension(
                name=self.alias,
                plugin=None, entry_point=None,
                obj=DiscoveryNodeIronicProvider)
        ]
        # test if it is an instance of DiscoveryNodeHLMProvider
        self.assertTrue(self.load_plugin() is DiscoveryNodeIronicProvider)

    @mock.patch("ironicclient.v1.node.NodeManager.list")
    @mock.patch("keystoneauth1.session.Session.get_endpoint")
    def test_pull_nodes(self, mock_get_endpoint, mock_node_list):
        """Test case regarding the instance after calling the load_plugin method.
        Test flow:
                >>> Creates a driver manager and stores it as a variable;
                >>> Creates a configuration and stores it as a variable;
                >>> Sets the configuration retry interval to 0;
                >>> Creates a driver node discovery with the configuration and the driver manager
                as parameters, and stores it as a variable;
                >>> Subscribes the listener to the driver node discovery;
                >>> Discovers the driver node discovery;
                >>> Sleeps to wait for the driver manager;
                >>> Checks if the listener and the driver manager have equal nodes; and,
                >>> Stops the thread.
        """
        ironic_nodes = FakeNodeIronic.fake_get_node_list()

        mock_node_list.return_value = ironic_nodes
        mock_get_endpoint.return_value = 'http://127.0.0.1:35357/v2.0'

        ovm_ironic = DiscoveryNodeIronicProvider(self.conf)
        # Subscribe a Listener
        ovm_ironic.subscribe(self.fake_listener)
        # Starting Thread component
        ovm_ironic.discover()

        sleep(3)
        self.assertEqual(len(self.fake_listener.nodes), 1)

        mock_node_list.return_value = []
        sleep(3)
        self.assertEqual(len(self.fake_listener.nodes), 0)

        ovm_ironic.stop()
        self.assertTrue(ovm_ironic._stopped)

    def load_plugin(self):
        """Loads the plugin to make possible the test of the load_plugin_get_nodes method.
        """
        return utils.load_class_by_alias(self.namespace, self.alias)
