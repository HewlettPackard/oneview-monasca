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
Tests of the Log module
"""

from base import TestBase
import oneview_monasca.shared.log as log


class TestLog(TestBase):
    """ Class that contains the unit tests of the Log module
    """
    def setUp(self):
        """Default set up method.
        """
        super(TestLog, self).setUp()
        self.log_name_base = 'test-log-base'
        self.log_base = log.get_logger(self.log_name_base)

    def tearDown(self):
        """Default tear down method.
        """
        super(TestLog, self).tearDown()

    def test_log_create_is_not_none(self):
        """Test case regarding the creation of a Log.
        Test flow:
                >>> Checks if the log instance if not None.
        """
        # testing if it is not none Instance
        self.assertNotEqual(self.log_base, None)

    def test_log__name_is_not_none(self):
        """Test case regarding if the log name is None.
        Test flow:
                >>> Checks if the log name is not None.
        """
        # testing if it is not None
        self.assertNotEqual(self.log_base.name, None)

    def test_log_name_is_not_empty(self):
        """Test case regarding if log name is empty.
        Test flow:
                >>> Checks if the log name is not empty.
        """
        # testing if it is not empty class name
        self.assertNotEqual(self.log_base.name, '')

    def test_log_is_class_name_equals_supposed_value(self):
        """Test case regarding the content of the log name.
        Test flow:
                >>> Checks if the log name is equal to itself.
        """
        # testing if it is equals to its supposed value
        self.assertEqual(self.log_base.name, self.log_name_base)

    def test_log_create_different_log(self):
        """Test case regarding if the log is equal to another log instance.
        Test flow:
                >>> Checks if the log instance is not equal to another log instance.
        """
        # testing if it is not equal to another log instance
        another_log = log.get_logger('another-log')
        self.assertNotEqual(self.log_base, another_log)
