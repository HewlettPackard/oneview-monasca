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

"""Unit test cases for the hlm plugin.
"""

from time import sleep
from base import TestBase
from tests.shared.config import Conf
from ovm_serverlist.shared import utils
from stevedore.extension import Extension
from ovm_serverlist.model.node import Node
from ovm_serverlist.model.metric import Metric
from tests.shared.fake import FakeComponentListener
from hpOneView.exceptions import HPOneViewException
from ovm_serverlist.manager.manager_oneview import ManagerOneView
from ovm_serverlist.driver.server_list import DiscoveryNodeServerListProvider

import os
import uuid
import mock


class TestServerList(TestBase):
    """This class test the hlm module from the ovm_serverlist.driver.
    """
    def setUp(self):
        """Set up environment to test.
        """
        super(TestServerList, self).setUp()
        self.alias = 'ovm_serverlist'
        self.namespace = 'node_discovery.driver'

        mac_file = '~' + os.path.sep + 'mac-file-test.yaml'
        self.mac_file = os.path.realpath(os.path.expanduser(mac_file))

        self.conf = Conf(self.mac_file)
        self.fake_component = FakeComponentListener()

    def tearDown(self):
        """TearDown tests.
        """
        super(TestServerList, self).tearDown()

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
                obj=DiscoveryNodeServerListProvider)
        ]
        # test if it is an instance of DiscoveryNodeHLMProvider
        self.assertTrue(self.load_plugin() is DiscoveryNodeServerListProvider)

    @mock.patch.object(ManagerOneView, 'get_server_hardware_uuid')
    def test_pull_nodes(self, mock_get_sh_uuid):
        """Test case regarding the instance after calling the load_plugin method.
        Test flow:
                >>> Create a mac file;
                >>> Loads the plugin;
                >>> Creates a listener;
                >>> Mock the get_server_hardware return value from Manager Oneview
                >>> Creates a driver manager and stores it as a variable;
                >>> Sets the configuration retry interval to 0;
                >>> Creates a driver node discovery with the configuration and the OneView
                fake manager as parameters;
                >>> Subscribes the listener to the driver node discovery;
                >>> Discovers the driver node discovery;
                >>> Sleeps to wait for the driver manager;
                >>> Checks if the listener and the driver manager have equal nodes; and,
                >>> Stops the thread;
                >>>Delete the mac file.
        """
        sh_mac, sh_uuid = '00:00:00:00:00:00', uuid.uuid4()

        # Writing in mac_file
        with open(self.mac_file, 'w') as mac_file:
            mac_file.write(
                'servers:\n' +
                '- mac-addr: ' + sh_mac +
                '\n  dimensions:\n       service: "compute"\n       hostname: "host_1"'
            )
            mac_file.close()

        mock_get_sh_uuid.return_value = sh_uuid
        server_list = DiscoveryNodeServerListProvider(self.conf)

        server_list.subscribe(self.fake_component)
        server_list.discover()

        sleep(3)
        metrics = {Metric(
            'oneview.server_hardware',
            {'service': 'compute', 'hostname': 'host_1', 'server_hardware_uuid': sh_uuid}
        )}
        self.assertIn(Node(sh_uuid, metrics), self.fake_component.nodes)

        mock_get_sh_uuid.return_value = []

        sleep(3)
        self.assertEqual(len(self.fake_component.nodes), 0)

        server_list.stop()
        os.remove(self.mac_file)

    @mock.patch.object(ManagerOneView, 'get_server_hardware_uuid')
    def test_fail_pull_nodes(self, mock_get_sh_uuid):
        sh_mac = '00:00:00:00:00:00'

        # Writing in mac_file
        with open(self.mac_file, 'w') as mac_file:
            mac_file.write(
                'servers:\n' +
                '- mac-addr: ' + sh_mac +
                '\n  dimensions:\n       service: "compute"\n       hostname: "host_1"'
            )
            mac_file.close()

        mock_get_sh_uuid.side_effect = HPOneViewException('response: 400')
        server_list = DiscoveryNodeServerListProvider(self.conf)

        server_list.subscribe(self.fake_component)
        server_list.discover()
        sleep(1)

        self.assertTrue(server_list._stopped)
        self.assertEqual(len(self.fake_component.nodes), 0)

    def test_error_to_load_mac_file(self):
        self.conf.serverlist.mac_file_path = '~/mac-file-test.yaml'
        server_list = DiscoveryNodeServerListProvider(self.conf)

        server_list.subscribe(self.fake_component)
        server_list.discover()
        sleep(1)

        self.assertTrue(server_list._stopped)
        self.assertEqual(len(self.fake_component.nodes), 0)

    def load_plugin(self):
        """Loads the plugin to make possible the test of the load_plugin_get_nodes method.
        """
        return utils.load_class_by_alias(self.namespace, self.alias)
