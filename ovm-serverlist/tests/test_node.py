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

"""Unit test cases for the node.py module.
 """

from ovm_serverlist.model.metric import Metric
from ovm_serverlist.model.node import Node
from base import TestBase

import ovm_serverlist.shared.constants as const


class TestNode(TestBase):
    """This class test the node module from the ovm_serverlist.model.
     """
    def setUp(self):
        """Setting up the tests.
        """
        super(TestNode, self).setUp()

    def tearDown(self):
        """Tearing down the tests.
        """
        super(TestNode, self).tearDown()

    def test_node_is_not_none(self):
        """Test case regarding it a node is None.
        Test flow:
                >>> Checks if a new node is not equal to None.
        """
        # testing if it is not none Instace
        self.assertNotEqual(Node(''), None)

    def test_node_name(self):
        """Test case regarding the name of a node.
        Test flow:
                >>> Creates a new node with "new-node" as parameter; and,
                >>> Checks if the new node has "new-node" as its name.
        """
        # testing if it name is supposed names
        node = Node('new-node')
        self.assertEquals(node.server_hardware_uuid, 'new-node')

    def test_node_metrics(self):
        """Test cases regarding node metrics.
        Test flow:
                >>> Creates a dimension dim1 based on a template constant;
                >>> Creates an attribute 'server_hardware_uuid' with the value '123' to
                this dim1;
                >>> Creates an attribute 'service' based on a service name
                constant to this dim1;
                >>> Creates a dimension dim2 based on a template constant;
                >>> Creates an attribute 'server_hardware_uuid' with the value '321' to
                dim2;
                >>> Creates an attribute 'service' based on a service name
                constant to dim2;
                >>> Creates a metric metric1 with "new-metric1" and dim1 as parameters;
                >>> Creates a metric metric2 with "new-metric2" and dim2 as parameters;
                >>> Creates a set of metrics and adds metric1 and metric2 to it;
                >>> Creates a node with 'uuid-server-hardware' and the metrics set as
                parameters;
                >>> Checks if the size of the collection of metrics of the node is equal to 2; and,
                >>> Checks if the nome name is equal to 'uuid-server-hardware';
        """
        # testing if it dimensions is supposed names
        dim1 = const.TEMPLATE_DIMENSIONS
        dim1['server_hardware_uuid'] = '123'
        dim1['service'] = const.SERVICE_NAME

        dim2 = const.TEMPLATE_DIMENSIONS
        dim2['server_hardware_uuid'] = '321'
        dim2['service'] = const.SERVICE_NAME

        metric1 = Metric('new-metric1', dim1)
        metric2 = Metric('new-metric2', dim2)
        metrics = set()
        metrics.add(metric1)
        metrics.add(metric2)

        node = Node('uuid-server-hardware', metrics)

        self.assertEquals(len(node.metrics), 2)
        self.assertEquals(node.server_hardware_uuid, 'uuid-server-hardware')

    def test_node_methods(self):
        """Test cases regarding the methods of the node object.
        Test flow:
                >>> Creates an empty metrics set;
                >>> Creates a node with 'uuid-server-hardware' and the metrics set as
                 parameters;
                >>> Checks if a node is equal to itself;
                >>> Checks if a node is not None;
                >>> Checks if a node is not equal to another one;
                >>> Checks if the __hash__ method has the same return when called twice; and,
                >>> Checks if the __repr__ method has the same return when called twice.
        """

        metrics = set()

        node = Node('uuid-server-hardware', metrics)

        self.assertTrue(node.__eq__(node))
        self.assertFalse(node.__eq__(None))
        self.assertFalse(node is Node('other_node', metrics))
        self.assertEquals(node.__hash__(), node.__hash__())
        self.assertEquals(node.__repr__(), node.__repr__())
