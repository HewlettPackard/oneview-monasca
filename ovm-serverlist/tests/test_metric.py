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

"""Unit test cases for the metric.py module.
"""

from ovm_serverlist.model.metric import Metric
from base import TestBase

import ovm_serverlist.shared.constants as const


class TestMetric(TestBase):
    """This class test the metric module from the ovm_serverlist.model.
    """
    def setUp(self):
        """Setting up the tests.
        """
        super(TestMetric, self).setUp()

    def tearDown(self):
        """Tearing down the tests.
        """
        super(TestMetric, self).tearDown()

    def test_metric_is_not_none(self):
        """Test case regarding if a metric is None.
        Test flow:
                >>> Checks if a new node is not equal to None.
        """
        # testing if it is not none Instace
        self.assertNotEqual(Metric(''), None)

    def test_metric_name(self):
        """Test case regarding the name of a metric.
        Test flow:
                >>> Creates a new node with "new-node" as parameter; and,
                >>> Checks if the new node has "new-node" as its name.
        """
        # testing if it name is supposed names
        metric = Metric('new-metric')
        self.assertEquals(metric.name, 'new-metric')

    def test_metric_dimensions(self):
        """Test cases regarding metrics dimensions.
        Test flow:
                >>> Creates dimensions based on a template constant;
                >>> Creates an attribute 'server_hardware_uuid' with the value '123' to
                the dimensions;
                >>> Creates an attribute 'service' based on a service name
                constant to the dimensions;
                >>> Creates a matric with 'new-metric' and the dimensions as parameters; and,
                >>> Checks if the metric dimensions are equal to the dimensions.
        """
        # testing if it dimensions is supposed names
        dimensions = const.TEMPLATE_DIMENSIONS
        dimensions['server_hardware_uuid'] = '123'
        dimensions['service'] = const.SERVICE_NAME

        metric = Metric('new-metric', dimensions)

        self.assertEquals(metric.dimensions, dimensions)

    def test_metric_methods(self):
        """Test cases regarding the methods of the metric object.
        Test flow:
                >>> Creates dimensions;
                >>> Creates a metric with 'new-metric' and the dimensions as
                parameters;
                >>> Checks if a metric is equal to itself;
                >>> Checks if a metric is not None;
                >>> Checks if a metric is not equal to another one;
                >>> Checks if the __hash__ method has the same return when called twice; and,
                >>> Checks if the __repr__ method has the same return when called twice.
        """

        dimensions = const.TEMPLATE_DIMENSIONS

        metric = Metric('new-metric', dimensions)

        self.assertTrue(metric.__eq__(metric))
        self.assertFalse(metric.__eq__(None))
        self.assertFalse(metric is Metric('other-metric', dimensions))
        self.assertEquals(metric.__hash__(), metric.__hash__())
        self.assertEquals(metric.__repr__(), metric.__repr__())
