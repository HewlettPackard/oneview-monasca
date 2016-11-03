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

"""Tests for the EventBus module.
"""

from oneview_monasca.eventbus.node_discovery import EventBUS
from oneview_monasca.eventbus.priority import PriorityENUM
from tests.shared.fake import FakeIronicPluginProvider
from tests.shared.fake import FakeHLMPluginProvider
from tests.shared.fake import FakeKeeper
from tests.shared.fake import FakePuller
from tests.shared.metric import Metric
from tests.shared.config import Conf
from tests.shared.node import Node
from base import TestBase

import mock


class TestEventBUS(TestBase):
    """ Class that contains the unit tests of the EventBus module.
    """
    def setUp(self):
        """ Default set up method.
        """
        super(TestEventBUS, self).setUp()
        self.eventbus = EventBUS(Conf())

    def tearDown(self):
        """ Default tear down method.
        """
        super(TestEventBUS, self).tearDown()
        self.eventbus.stop()

    def test_eventbus_create(self):
        """Test case regarding the creation of an event bus.
        Test flow:
                >>> Checks if the eventbus is not None.
        """
        # testing if it is not none Instance
        self.assertNotEqual(self.eventbus, None)

    def test_subscribers(self):
        """Test cases regarding the subscribes.
        Test flow:
                >>> Creates a fake puller and stores it in comp_low;
                >>> Creates a fake keeper and stores it in comp_high;
                >>> Checks if the subscribers set is empty;
                >>> Subscribes comp_low;
                >>> Checks if the subscribers set has one subscriber with low priority;
                >>> Checks if the subscribers set has no subscriber with high priority;
                >>> Subscribes comp_high with a high priority;
                >>> Checks if the subscribers set has one subscriber with low priority;
                >>> Checks if the subscribers set has one subscriber with high priority;
                >>> Checks if the subscribers set length is 2;
                >>> Unsubscribe comp_low;
                >>> Checks if the subscribers set has no subscriber with low priority;
                >>> Checks if the subscribers set length is 1;
                >>> Unsubscribe comp_high;
                >>> Checks if the subscribers set has no subscriber with high priority;
                and,
                >>> Checks if the subscribers set is empty;
        """
        comp_low = FakePuller()
        comp_high = FakeKeeper()
        # Verify if is empty set
        self.assertEqual(self.eventbus.length_subscribers(PriorityENUM.LOW), 0)
        self.assertEqual(self.eventbus.length_subscribers(PriorityENUM.HIGH), 0)
        self.eventbus.subscribe(comp_low)
        # Verify if contains one subscribe
        self.assertEqual(self.eventbus.length_subscribers(PriorityENUM.LOW), 1)
        # Verify if contains zero subscribe
        self.assertEqual(self.eventbus.length_subscribers(PriorityENUM.HIGH), 0)
        self.eventbus.subscribe(comp_high, PriorityENUM.HIGH)
        # Verify if contains one subscribe to each priority
        self.assertEqual(self.eventbus.length_subscribers(PriorityENUM.LOW), 1)
        self.assertEqual(self.eventbus.length_subscribers(PriorityENUM.HIGH), 1)
        # Verify if contains two subscribe
        self.assertEqual(self.eventbus.length_subscribers(), 2)
        self.eventbus.unsubscribe(comp_low)
        # Verify is contains zero subscribe to low priority
        self.assertEqual(self.eventbus.length_subscribers(PriorityENUM.LOW), 0)
        # Verify is contains one subscribe
        self.assertEqual(self.eventbus.length_subscribers(), 1)
        self.eventbus.unsubscribe(comp_high)
        # Verify is contains zero subscribe to high priority
        self.assertEqual(self.eventbus.length_subscribers(PriorityENUM.HIGH), 0)
        # Verify is not exists subscribe
        self.assertEqual(self.eventbus.length_subscribers(), 0)

    def test_simple_multiples_metrics(self):
        """Test cases regarding simple and multiple metrics.
        Overview of test flow:
                >>> Creates fake components;
                >>> Subscribes eventbuvs in the fake puglins;
                >>> Subscribes the fake publisher in the eventbus;
                >>> Creates fake nodes to the fake components;
                >>> Sends events with the nodes;
                >>> Checks if the publisher collection of nodes is equal to the
                supposed collection;
                >>> For each node:
                        >>> Checks if the metrics length is 2;
        """
        # Create fake components
        plugin_hlm = FakeHLMPluginProvider()
        plugin_ironic = FakeIronicPluginProvider()
        puller = FakePuller()
        # Subscribe eventbus in plugins
        plugin_hlm.subscribe(self.eventbus)
        plugin_ironic.subscribe(self.eventbus)
        # Subscribe publisher in eventbus
        self.eventbus.subscribe(puller)

        # Test if metrics is group by server hardware UUID ##
        # Create fake node to Ironic Plugin
        ironic_nodes = self.create_fake_node_plugin('server_hardware_uuid', 'ironic')
        # Create fake node to HLM Plugin (compute)
        compute_nodes = self.create_fake_node_plugin('server_hardware_uuid', 'compute')
        # Create fake node to HLM Plugin (storage)
        storage_nodes = self.create_fake_node_plugin('server_hardware_uuid', 'storage')
        # Create fake node to HLM Plugin (control plane)
        control_plane_nodes = self.create_fake_node_plugin('server_hardware_uuid', 'control plane')

        # Send event with ironic nodes
        plugin_ironic.available({ironic_nodes})
        nodes = {ironic_nodes}
        self.assertEqual(puller.get_nodes(), nodes)

        # Send event with compute nodes
        plugin_hlm.available({compute_nodes})
        ironic_nodes.metrics.update(compute_nodes.metrics)
        node = ironic_nodes
        nodes = {node}
        self.assertEqual(puller.get_nodes(), nodes)

        # Send event with storage nodes
        plugin_hlm.available({storage_nodes})
        ironic_nodes.metrics.update(storage_nodes.metrics)
        node = ironic_nodes
        nodes = {node}
        self.assertEqual(puller.get_nodes(), nodes)

        # Send event with control plane nodes
        plugin_hlm.available({control_plane_nodes})
        ironic_nodes.metrics.update(control_plane_nodes.metrics)
        node = ironic_nodes
        nodes = {node}
        self.assertEqual(puller.get_nodes(), nodes)

        # test if contains one node only
        self.assertEqual(len(puller.get_nodes()), 1)

        for node in puller.get_nodes():
            # test if contains four metrics (ironic, compute, storage, control plane)
            self.assertEqual(len(node.metrics), 4)

        # Send event with unavailable compute node
        plugin_hlm.unavailable({compute_nodes})
        ironic_nodes.metrics.difference_update(compute_nodes.metrics)
        node = ironic_nodes
        nodes = {node}
        self.assertEqual(puller.get_nodes(), nodes)

        # Send event with unavailable storage node
        plugin_hlm.unavailable({storage_nodes})
        ironic_nodes.metrics.difference_update(storage_nodes.metrics)
        node = ironic_nodes
        nodes = {node}
        self.assertEqual(puller.get_nodes(), nodes)

        for node in puller.get_nodes():
            # test if contains two metrics (ironic, control plane)
            self.assertEqual(len(node.metrics), 2)

        # Send event with unavailable control plane node
        plugin_hlm.unavailable({control_plane_nodes})
        ironic_nodes.metrics.difference_update(control_plane_nodes.metrics)
        node = ironic_nodes
        nodes = {node}
        self.assertEqual(puller.get_nodes(), nodes)

        # Send event with unavailable ironic node
        plugin_hlm.unavailable({ironic_nodes})
        ironic_nodes.metrics.difference_update(ironic_nodes.metrics)
        node = ironic_nodes
        nodes = set()
        self.assertEqual(puller.get_nodes(), nodes)

    def test_complex_multiples_metrics(self):
        """Test cases regarding complex multiple metrics.
        Overview of test flow:
                >>> Creates fake components;
                >>> Subscribes eventbuvs in the fake puglins;
                >>> Subscribes the fake publisher in the eventbus;
                >>> Creates fake nodes to the fake components;
                >>> Sends events with the nodes;
                >>> Checks if the publisher collection of nodes is equal to the
                supposed collection;
                >>> For each node:
                        >>> Checks if the metrics length is 27;
        """
        # Create fake components
        plugin_hlm = FakeHLMPluginProvider()
        plugin_ironic = FakeIronicPluginProvider()
        puller = FakePuller()
        # Subscribe eventbus in plugins
        plugin_hlm.subscribe(self.eventbus)
        plugin_ironic.subscribe(self.eventbus)
        # Subscribe publisher in eventbus
        self.eventbus.subscribe(puller)

        # Test if metrics is group by server hardware UUID ##
        # Create fake node to Ironic Plugin
        ironic_nodes = self.create_fake_node_plugin('server_hardware_uuid', 'ironic', 7)
        # Create fake node to HLM Plugin (compute)
        compute_nodes = self.create_fake_node_plugin('server_hardware_uuid', 'compute', 20)

        # Send event with ironic nodes
        plugin_ironic.available({ironic_nodes})
        nodes = {ironic_nodes}
        self.assertEqual(puller.get_nodes(), nodes)

        # Send event with compute nodes
        plugin_hlm.available({compute_nodes})
        ironic_nodes.metrics.update(compute_nodes.metrics)
        node = ironic_nodes
        nodes = {node}
        self.assertEqual(puller.get_nodes(), nodes)

        for node in puller.get_nodes():
            # test if contains two metrics (ironic, control plane)
            self.assertEqual(len(node.metrics), 27)

        # Create fake node to HLM Plugin (compute)
        compute_nodes = self.create_fake_node_plugin('server_hardware_uuid', 'compute', 10)
        # Send event with unavailable compute nodes
        plugin_hlm.unavailable({compute_nodes})
        ironic_nodes.metrics.difference_update(compute_nodes.metrics)
        node = ironic_nodes
        nodes = {node}
        self.assertEqual(puller.get_nodes(), nodes)

        for node in puller.get_nodes():
            # test if contains two metrics (ironic, control plane)
            self.assertEqual(len(node.metrics), 17)

    def test_priority_events(self):
        """Test cases regarding the events priority.
        Test flow:
                >>> Creates fake components;
                 >>> Subscribes eventbuvs in the fake puglins;
                >>> Subscribes the fake publisher in the eventbus;
                >>> Creates fake nodes to the fake components;
                >>> Sends events with the nodes;
                >>> Checks if the publisher collection of nodes is equal to the
                supposed collection;
        """
        # Create fake components
        plugin_ironic = FakeIronicPluginProvider()
        plugin_hlm = FakeHLMPluginProvider()
        puller = FakePuller()
        keeper = FakeKeeper()
        # Subscribe eventbus in plugins
        plugin_hlm.subscribe(self.eventbus)
        plugin_ironic.subscribe(self.eventbus)
        # Subscribe publisher in eventbus
        self.eventbus.subscribe(puller)
        self.eventbus.subscribe(keeper, PriorityENUM.HIGH)

        # Create fake node to Ironic Plugin
        ironic_nodes = self.create_fake_node_plugin('server_hardware_uuid', 'ironic')
        # Create fake node to Compute Plugin
        compute_nodes = self.create_fake_node_plugin('server_hardware_uuid', 'compute')

        # Send event with available ironic nodes #
        plugin_ironic.available({ironic_nodes})
        # Checking if the Metric Keeper is the first to received event
        self.assertTrue(keeper.last_updated < puller.last_updated)

        # Send event with available compute nodes #
        plugin_hlm.available({compute_nodes})
        # Checking if the Metric Keeper is the first to received event
        self.assertTrue(keeper.last_updated < puller.last_updated)

        # Send event with unavailable ironic nodes #
        plugin_hlm.unavailable({ironic_nodes})
        # Checking if the Metric Keeper is the first to received event
        self.assertTrue(keeper.last_updated > puller.last_updated)

        # Send event with unavailable compute nodes #
        plugin_hlm.unavailable({compute_nodes})
        # Checking if the Metric Keeper is the first to received event
        self.assertTrue(keeper.last_updated > puller.last_updated)

    @staticmethod
    def create_fake_node_plugin(server_hardware_uuid, service, len_metrics=1):
        """Creates a fake plugin node to make possible the tests.
        """
        metric_name = 'oneview.server_hardware'
        metrics = set()
        for i in range(len_metrics):
            dimensions = {'service': service}
            if len_metrics > 1:
                dimensions['something-dimension'] = i
            metrics.add(Metric(metric_name, dimensions))

        return Node(server_hardware_uuid, metrics)

    @mock.patch('oneview_monasca.shared.utils.list_names_driver')
    def test_start_event_bus(self, mock_drivers):
        """Test case regarding the start method.
        """
        raised = False
        mock_drivers.return_value = []

        try:
            self.eventbus.start()
        except:
            raised = True
        self.assertFalse(raised)
