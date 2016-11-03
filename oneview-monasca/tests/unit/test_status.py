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
Tests of the Status module
"""

from oneview_monasca.model.status import Status
from datetime import datetime
from base import TestBase

import oneview_monasca.shared.constants as const
import time


class TestStatus(TestBase):
    """ Class that contains the unit tests of the Status module
    """
    def setUp(self):
        """Default set up method.
        """
        super(TestStatus, self).setUp()
        self.server_hardware_uuid = '123-abc'
        self.status = const.METRIC_VALUE_PARSER['OK']
        self.modified_timestamp = datetime.now()

    def tearDown(self):
        """Default tear down method.
        """
        super(TestStatus, self).tearDown()

    def test_status_create_is_not_none(self):
        """Test case regarding the creation of a status.
        Test flow:
                >>> Creates a status; and,
                >>> Checks if the log instance if not None.
        """
        # testing if it is not none Instance
        status = Status(
            self.server_hardware_uuid,
            self.status,
            self.modified_timestamp
        )
        self.assertNotEqual(status, None)

    def test_status_fields(self):
        """Test case regarding the status fields.
        Test flow:
                >>> Creates a status; and,
                >>> Checks if the status values are equal to their supposed value.
        """
        status = Status(
            self.server_hardware_uuid,
            self.status,
            self.modified_timestamp
        )
        # testing if fields is supposed values
        self.assertEqual(status.server_hardware_uuid, self.server_hardware_uuid)
        self.assertEqual(status.status, self.status)
        self.assertEqual(status.modified_timestamp, self.modified_timestamp)

    def test_status_eq(self):
        """Test to compare status using the __eq__ method.
        Test flow:
        """
        server_hardware_uuid1 = '123-abc'
        server_hardware_uuid2 = '321-abc'
        timestamp = time.time()

        status1 = Status(server_hardware_uuid1, 1, timestamp)
        status2 = Status(server_hardware_uuid2, 2, timestamp)
        status3 = Status(server_hardware_uuid1, 1, timestamp)
        status4 = Status(server_hardware_uuid2, 2, timestamp)

        self.assertFalse(status1.__eq__(status2))
        self.assertTrue(status1.__eq__(status3))
        self.assertFalse(status2.__eq__(status3))
        self.assertTrue(status2.__eq__(status4))

        self.assertFalse(status1.__eq__(timestamp))

    def test_status_hash(self):
        """Test to check __hash__ method.
        Test flow:
        """

        server_hardware_uuid1 = '123-abc'
        server_hardware_uuid2 = '321-abc'
        timestamp = time.time()

        status1 = Status(server_hardware_uuid1, 1, timestamp)
        status2 = Status(server_hardware_uuid2, 2, timestamp)

        self.assertEqual(status1.__hash__(), status1.__hash__())
        self.assertEqual(status2.__hash__(), status2.__hash__())
        self.assertNotEqual(status1.__hash__(), status2.__hash__())

    def test_status_repr(self):
        """Test to check __repr__ method.
        Test flow:
        """
        server_hardware_uuid1 = '123-abc'
        server_hardware_uuid2 = '321-abc'
        timestamp = time.time()

        status1 = Status(server_hardware_uuid1, 1, timestamp)
        status2 = Status(server_hardware_uuid2, 2, timestamp)

        self.assertEqual(status1.__repr__(), status1.__repr__())
        self.assertEqual(status2.__repr__(), status2.__repr__())
        self.assertNotEqual(status1.__repr__(), status2.__repr__())
