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

""" This module provides unit tests for the Puller class
"""

from oneview_monasca.manager.manager_oneview import ManagerOneView
from oneview_monasca.eventbus.node_discovery import EventBUS
from oneview_monasca.publisher.puller import Puller
from tests.shared.fake import FakeIronicPluginProvider
from tests.shared.fake import FakeKeeper
from tests.shared.metric import Metric
from tests.shared.config import Conf
from tests.shared.node import Node
from base import TestBase
from time import sleep

import mock


class TestPuller(TestBase):
    """ Class that contains the Puller unit tests.
    """
    def setUp(self):
        """ Set up the Puller and other objects that will be used
        into the tests cases.
        """
        super(TestPuller, self).setUp()
        self.conf = Conf()
        self.manager_oneview = ManagerOneView(None, None, None)
        self.puller = Puller(self.manager_oneview, self.conf.DEFAULT.periodic_refresh_interval, mock.MagicMock())

        # self.puller._first_available_iteration = False
        self.eventbus = EventBUS(self.conf)

    def tearDown(self):
        """ Default tear down method.
        """
        super(TestPuller, self).tearDown()

    @staticmethod
    def create_fake_node_plugin(server_hardware_uuid, service, len_metrics=1):
        """ Method that create a fake node to be used into tests.

        :param server_hardware_uuid: String. Fake Server Hardware uuid.
        :param service: String to indicate the service.
        :param len_metrics: Integer to set up the length of the set of metrics.
        """
        metric_name = 'oneview.server_hardware'
        metrics = set()
        for i in range(len_metrics):
            dimensions = {'service': service}
            if len_metrics > 1:
                dimensions['something-dimension'] = i
            metrics.add(Metric(metric_name, dimensions))

        return Node(server_hardware_uuid, metrics)

    @mock.patch.object(ManagerOneView, 'get_server_hardware_status', side_effect=Exception)
    def test_process_status(self, mock_manager):
        """ Test cases regarding the flows of status objects into the Puller.
            Test flow:
                    >>> Create fake components and a fake node. Force a plugin to discover the new node.
                    >>> Verify if the status objects has been created and sent to fake keeper.
                    When the agent starts, only into the first node discover, the puller should
                    process and send status to keeper.
                    >>> Discover another node. Ensure that is no sent to keeper.
        """
        # Create fake components
        plugin_ironic = FakeIronicPluginProvider()
        keeper = FakeKeeper()

        self.puller.subscribe(keeper)
        # Subscribe eventbus in plugins
        plugin_ironic.subscribe(self.eventbus)

        # Subscribe publisher in eventbus
        self.eventbus.subscribe(self.puller)

        # Create fake node to Ironic Plugin
        ironic_nodes = self.create_fake_node_plugin('server_hardware_uuid', 'ironic')

        # Send event with available ironic nodes
        plugin_ironic.available({ironic_nodes})

        self.assertTrue(mock_manager.called)
        self.assertEqual(len(keeper.states), 0)

        # Unavailable fake node
        plugin_ironic.unavailable({ironic_nodes})
        self.assertEqual(len(self.puller._monitored_nodes), 0)

        # Create a second fake node to Ironic Plugin
        ironic_nodes = self.create_fake_node_plugin('server_hardware_uuid2', 'ironic', 2)

        mock_manager.side_effect = None
        self.puller._first_available_iteration = True
        mock_manager.return_value = (3, '2014-08-07T11:00:11.467Z')

        # Send a second event with the new node
        plugin_ironic.available({ironic_nodes})

        mock_manager.ssert_called_with(ironic_nodes.server_hardware_uuid)
        self.assertEqual(len(keeper.states), 1)

    @mock.patch.object(ManagerOneView, 'get_server_hardware_status', return_value=(3, '2014-08-07T11:00:11.467Z'))
    def test_process_status_with_starting_thread(self, mock_manager):
        """ Test cases regarding the flows of status objects into the Puller.
            Test flow:
                    >>> Create fake components and a fake node. Force a plugin to discover the new node.
                    >>> Verify if the status objects has been created and sent to fake keeper.
                    >>> Start the puller thread and verify if it yet send metric objects.
        """
        # Create fake components
        plugin_ironic = FakeIronicPluginProvider()
        keeper = FakeKeeper()

        self.puller.subscribe(keeper)
        # Subscribe eventbus in plugins
        plugin_ironic.subscribe(self.eventbus)

        # Subscribe publisher in eventbus
        self.eventbus.subscribe(self.puller)

        # Staring Puller
        self.puller.publish()

        # Create fake node to Ironic Plugin
        ironic_nodes = self.create_fake_node_plugin('server_hardware_uuid', 'ironic', 2)

        # Send a second event with the new node
        plugin_ironic.available({ironic_nodes})
        sleep(5)

        # Stopping Puller
        self.puller.stop()

        mock_manager.ssert_called_with(ironic_nodes.server_hardware_uuid)
        self.assertEqual(len(keeper.states), 1)
