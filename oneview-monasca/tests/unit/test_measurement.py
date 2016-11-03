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

"""Unit test cases for the measurement.py module.
"""

from oneview_monasca.model.measurement import Measurement
from base import TestBase


class TestMeasurement(TestBase):
    """This class test the measurement module from the oneview_monasca.model.
    """
    def setUp(self):
        """Setting up the tests.
        """
        super(TestMeasurement, self).setUp()

    def tearDown(self):
        """Tearing down the tests.
        """
        super(TestMeasurement, self).tearDown()

    def test_measurement_is_not_none(self):
        """Test case regarding if a measurement is None.
        Test flow:
                >>> Check if a measurement is not None
        """
        self.assertNotEqual(Measurement('', ''), None)

    def test_create_measurement(self):
        """Test the creation of valid measurements.
        Test flow:
                >>> Create a measurement with empty dictionary for value_meta
                >>> Create a measurement with empty dictionary for dimensions
                >>> Create a measurement with only required parameters.
                >>> Create a measurement with all parameters
                >>> Verify if dimensions and value_meta are empty
                >>> Verify that timestamp is not None
        """
        measure1 = Measurement(
            'oneview.health_status', 1,
            dimensions={'host': 'localhost'}
        )

        measure2 = Measurement(
            'oneview.health_status', 2,
            value_meta={'alarm': 'url'}
        )

        measure3 = Measurement('oneview.health_status', 3)

        measure4 = Measurement(
            name='oneview.health_status',
            value=4,
            dimensions={'host': 'localhost'},
            value_meta={'alarm': 'url'}
        )

        self.assertEquals(measure1.value_meta, {})
        self.assertEquals(measure2.dimensions, {})
        self.assertEquals(measure3.dimensions, {})
        self.assertEquals(measure3.value_meta, {})
        self.assertNotEqual(measure4.dimensions, {})
        self.assertNotEqual(measure4.value_meta, {})

        self.assertNotEqual(measure1.timestamp, None)
        self.assertNotEqual(measure2.timestamp, None)
        self.assertNotEqual(measure3.timestamp, None)
        self.assertNotEqual(measure4.timestamp, None)

    def test_measurements_eq(self):
        """Test to compare measurements using the __eq__ method.
        Test flow:
        """

        measure1 = Measurement('oneview.health_status', 1)
        measure2 = Measurement('oneview.health_status', 2)
        measure3 = Measurement('health_status', 2)
        measure4 = Measurement(
            'health_status',
            value=1, dimensions={'host': 'localhost'}
        )
        measure5 = Measurement(
            'oneview', value=2,
            dimensions={'host': 'localhost2'}
        )
        measure6 = Measurement(
            'health', value=3,
            dimensions={'host': 'local'}, value_meta={'alarm': 'a'}
        )
        measure7 = Measurement(
            'health2', value=3,
            dimensions={'host': 'local'}, value_meta={'alarm': 'a'}
        )

        self.assertNotEqual(measure1, measure2)
        self.assertEquals(measure2, measure3)
        self.assertNotEquals(measure4, measure5)
        self.assertEquals(measure6, measure7)

        self.assertFalse(measure1.__eq__(0))
