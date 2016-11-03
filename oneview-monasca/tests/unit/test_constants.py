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
Tests of Constants module.
"""

from base import TestBase
from oneview_monasca.shared import constants


class TestConstants(TestBase):
    """This class test the pase_command module from oneview_monasca.shared.
    """
    def setUp(self):
        """Setting up the tests.
        """
        super(TestConstants, self).setUp()

    def tearDown(self):
        """Tearing down the tests.
        """
        super(TestConstants, self).tearDown()

    # this functions tests the constant APPLICATION_NAME
    def test_application_name(self):
        """Test cases regarding the APPLICATION_NAME constant.
        Test flow:
                >>> Checks if the constant is equal to itself;
                >>> Checks if the constant is equal to its supposed value;
                >>> Checks if the constant is not empty;
                >>> Checks if the constant it not an aleatory value; and,
                >>> Checks if the constant is not None.
        """
        # testing if it is equals to it self
        self.assertEqual(constants.APPLICATION_NAME, constants.APPLICATION_NAME)
        # testing if it is equals to its supposed value
        self.assertEqual(constants.APPLICATION_NAME, 'monasca_oneviewd')
        # testing if it is not empty
        self.assertNotEqual(constants.APPLICATION_NAME, '')
        # testing if it is not equals to aleatory string
        self.assertNotEqual(constants.APPLICATION_NAME, 'test')
        # testing if it is not null
        self.assertNotEqual(constants.APPLICATION_NAME, None)

    # this function tests the constant METRIC_NAME
    def test_metric_name(self):
        """Test cases regarding the METRIC_NAME constant.
        Test flow:
                >>> Checks if the constant is equal to itself;
                >>> Checks if the constant is equal to its supposed value;
                >>> Checks if the constant is not empty;
                >>> Checks if the constant it not an aleatory value; and,
                >>> Checks if the constant is not None.
        """
        self.assertEqual(constants.METRIC_NAME, constants.METRIC_NAME)
        # testing if it is equals to its supposed value
        self.assertEqual(constants.METRIC_NAME, 'oneview.node_status')
        # testing if it is not empty
        self.assertNotEqual(constants.METRIC_NAME, '')
        # testing if it is not equals to aleatory string
        self.assertNotEqual(constants.METRIC_NAME, 'test')
        # testing if it is not null
        self.assertNotEqual(constants.METRIC_NAME, None)

    # this function tests the constant PREFIX_ID_COORD
    def test_coordinator_prefix_id(self):
        """Test cases regarding the PREFIX_ID_COORD constant.
        Test flow:
                >>> Checks if the constant is equal to itself;
                >>> Checks if the constant is equal to its supposed value;
                >>> Checks if the constant is not empty;
                >>> Checks if the constant it not an aleatory value; and,
                >>> Checks if the constant is not None.
        """
        self.assertEqual(constants.PREFIX_ID_COORD, constants.PREFIX_ID_COORD)
        # testing if it is equals to its supposed value
        self.assertEqual(constants.PREFIX_ID_COORD, b'oneviewd')
        # testing if it is not empty
        self.assertNotEqual(constants.PREFIX_ID_COORD, '')
        # testing if it is not equals to aleatory string
        self.assertNotEqual(constants.PREFIX_ID_COORD, 'test')
        # testing if it is not null
        self.assertNotEqual(constants.PREFIX_ID_COORD, None)

    # this function tests the constant HEARTBEAT_INTERVAL
    def test_coordinator_heartbeat_interval(self):
        """Test cases regarding the HEARTBEAT_INTERVAL constant.
        Test flow:
                >>> Checks if the constant is equal to itself;
                >>> Checks if the constant is equal to its supposed value;
                >>> Checks if the constant is not empty;
                >>> Checks if the constant it not an aleatory value; and,
                >>> Checks if the constant is not None.
        """
        self.assertEqual(constants.HEARTBEAT_INTERVAL, constants.HEARTBEAT_INTERVAL)
        # testing if it is equals to its supposed value
        self.assertEqual(constants.HEARTBEAT_INTERVAL, 1)
        # testing if it is not empty
        self.assertNotEqual(constants.HEARTBEAT_INTERVAL, 3)
        # testing if it is not equals to aleatory string
        self.assertNotEqual(constants.HEARTBEAT_INTERVAL, 0)
        # testing if it is not null
        self.assertNotEqual(constants.HEARTBEAT_INTERVAL, None)

    # this function tests the constant FORMATTER_LOG
    def test_log_output(self):
        """Test cases regarding the FORMATTER_LOG constant.
        Test flow:
                >>> Checks if the constant is equal to itself;
                >>> Checks if the constant is equal to its supposed value;
                >>> Checks if the constant is not empty;
                >>> Checks if the constant it not an aleatory value; and,
                >>> Checks if the constant is not None.
        """
        self.assertEqual(constants.FORMATTER_LOG, constants.FORMATTER_LOG)
        # testing if it is equals to its supposed value
        self.assertEqual(constants.FORMATTER_LOG, '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # testing if it is not empty
        self.assertNotEqual(constants.FORMATTER_LOG, '')
        # testing if it is not equals to aleatory string
        self.assertNotEqual(constants.FORMATTER_LOG, 'test')
        # testing if it is not null
        self.assertNotEqual(constants.FORMATTER_LOG, None)

    # this function tests the constant HTTP_ERROR_400
    def test_http_error(self):
        """Test cases regarding the HTTP_ERROR_400 constant.
        Test flow:
                >>> Checks if the constant is equal to itself;
                >>> Checks if the constant is equal to its supposed value;
                >>> Checks if the constant is not empty;
                >>> Checks if the constant it not an aleatory value; and,
                >>> Checks if the constant is not None.
        """
        self.assertEqual(constants.HTTP_ERROR_400, constants.HTTP_ERROR_400)
        # testing if it is equals to its supposed value
        self.assertEqual(constants.HTTP_ERROR_400, 'response: 400')
        # testing if it is not empty
        self.assertNotEqual(constants.HTTP_ERROR_400, '')
        # testing if it is not equals to aleatory string
        self.assertNotEqual(constants.HTTP_ERROR_400, 'test')
        # testing if it is not null
        self.assertNotEqual(constants.HTTP_ERROR_400, None)
