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

""" This test module covers Keeper component.
"""
from oneview_monasca.manager.manager_oneview import ManagerOneView
from oneview_monasca.manager.manager_monasca import ManagerMonasca
from oneview_monasca.eventbus.node_discovery import EventBUS
from oneview_monasca.eventbus.priority import PriorityENUM
from oneview_monasca.model.measurement import Measurement
from oneview_monasca.publisher.keeper import Keeper
from oneview_monasca.model.status import Status

from tests.shared.config import Conf
from tests.shared.config import ConfOneview
from tests.shared.fake import FakeModelMetric, FakeModelNode
from base import TestBase
from datetime import datetime

import mock
import time


class TestKeeper(TestBase):
    """
    This class test Keeper component.
    """
    def setUp(self):
        """
        Setting up the variables.
        Creating an object Keeper.
        """
        super(TestKeeper, self).setUp()

        conf = ConfOneview()
        oneview_manager = ManagerOneView(conf.host, conf.username, conf.password, conf.max_attempt)
        monasca_manager = ManagerMonasca(None, None, None, None, None)

        self.keeper = Keeper(oneview_manager, monasca_manager, batch_time="2")

    def tearDown(self):
        """
        Tearing down the objects.
        """
        super(TestKeeper, self).tearDown()
        self.keeper.stop()

    @mock.patch.object(ManagerMonasca, 'send_metrics')
    def test_keeper_publish(self, mock_manager):
        """ Test the created instance of Keeper
        Test flow:
               >>> Test if the object is not None.
               >>> Test if have empty metric_storage.
        """
        self.keeper.publish()
        self.assertFalse(self.keeper._stopped)
        self.assertEqual(self.keeper._metric_storage, {})
        self.assertEqual(self.keeper._metric_storage.items(), [])
        self.assertEqual(self.keeper._metric_storage.keys(), [])
        self.assertEqual(self.keeper._metric_storage.values(), [])

        eventbus = EventBUS(Conf())
        eventbus.subscribe(self.keeper, PriorityENUM.HIGH)

        # Create single Metric
        metric = FakeModelMetric('mymetric', {'key1': 'value1', 'key2': 'value2'})
        node = FakeModelNode('uuid_1', {metric})
        # Create a resource status
        resource = Status('uuid_1', 0, datetime.now())

        # Receive a new status_update of not monitored resource
        self.keeper.status_update({resource})

        # Available information for Keeper
        eventbus.available({node})
        # Receive a new status_update of monitored resource
        time.sleep(1)
        self.keeper.status_update({resource})

        time.sleep(5)
        self.keeper.stop()

        measurement = Measurement(metric.name, resource.status, metric.dimensions, {})
        mock_manager.assert_called_with([measurement])

    @mock.patch.object(ManagerMonasca, 'send_metrics')
    def test_available_with_single_value(self, mock_manager):
        """ Test if Keeper will have all information that have been sent.
        Test flow:
               >>> Create a EventBUS and subscribe the Keeper
               >>> Create one Metric for one Node
               >>> Let the node be available in the EventBUS
               >>> Keeper should contain all information about the Node
               >>> Send the same node in available in the EventBUS
               >>> Keeper should have same information
               >>> Send status update for the Node in the EventBUS
               >>> Keeper will update the metric_storage with the information
               >>> Send unavailable in EventBUS with the Node
               >>> Keeper will not have any information about the Node.
        """
        eventbus = EventBUS(Conf())
        eventbus.subscribe(self.keeper, PriorityENUM.HIGH)

        # Create single Metric
        metric_set = set()
        metric = FakeModelMetric('mymetric', {'key1': 'value1', 'key2': 'value2'})
        metric_set.add(metric)
        nodes = set()
        nodes.add(FakeModelNode('uuid_1', metric_set))
        # Create Status
        states = set()
        status = Status('uuid_1', 0, datetime.now())
        states.add(status)
        # Available information for Keeper
        eventbus.available(nodes)
        self.assertNotEqual(self.keeper._metric_storage, {})
        self.assertEqual(self.keeper._metric_storage.keys(), ['uuid_1'])
        self.assertNotEqual(self.keeper._metric_storage.values(), [])
        self.assertEqual(len(self.keeper._metric_storage.values()), 1)
        self.assertEqual(len(self.keeper._metric_storage['uuid_1'].keys()), 3)
        self.assertItemsEqual(self.keeper._metric_storage['uuid_1'].keys(), ['metrics', 'status', 'meta'])
        self.assertEqual(self.keeper._metric_storage['uuid_1']['status'], None)
        self.assertEqual(type(self.keeper._metric_storage['uuid_1']['metrics']), set)
        self.assertEqual(len(self.keeper._metric_storage['uuid_1']['metrics']), 1)
        self.assertEqual(self.keeper._metric_storage['uuid_1']['meta'], {})

        metric_object = next(iter(self.keeper._metric_storage['uuid_1']['metrics']))
        self.assertEqual(metric_object.name, metric.name)
        self.assertItemsEqual(metric_object.dimensions, metric.dimensions)

        # Update current Keeper information
        eventbus.available(nodes)
        self.assertNotEqual(self.keeper._metric_storage, {})
        self.assertEqual(self.keeper._metric_storage.keys(), ['uuid_1'])
        self.assertNotEqual(self.keeper._metric_storage.values(), [])

        # Receive status_update
        self.keeper.status_update(states)
        self.assertEqual(self.keeper._metric_storage['uuid_1']['status'].status, 0)
        self.assertEqual(
            self.keeper._metric_storage['uuid_1']['status'].modified_timestamp,
            status.modified_timestamp
        )
        self.assertEqual(
            self.keeper._metric_storage['uuid_1']['status'].server_hardware_uuid,
            status.server_hardware_uuid
        )
        # Unavailable information for Keeper
        eventbus.unavailable(nodes)

        self.assertEqual(self.keeper._metric_storage, {})
        self.assertEqual(self.keeper._metric_storage.items(), [])
        self.assertEqual(self.keeper._metric_storage.keys(), [])
        self.assertEqual(self.keeper._metric_storage.values(), [])
