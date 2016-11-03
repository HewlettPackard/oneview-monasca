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
from oneview_monasca.shared import exceptions


class TestExceptions(TestBase):
    """ Class that contains the unit tests of the Log module
    """
    def setUp(self):
        """Default set up method.
        """
        super(TestExceptions, self).setUp()

    def tearDown(self):
        """Default tear down method.
        """
        super(TestExceptions, self).tearDown()

    def test_login_fail(self):
        """Test case regarding the LoginFailException.
        Test flow:
        """
        log = exceptions.LoginFailException('Exception LoginFailException raised')
        self.assertEqual(log.message, 'Exception LoginFailException raised')

    def test_httpd_fail(self):
        """Test case regarding the HTTPFailException.
        Test flow:
        """
        log = exceptions.HTTPFailException('Exception HTTPFailException raised')
        self.assertEqual(log.message, 'Exception HTTPFailException raised')

    def test_scmb_connection_fail(self):
        """Test case regarding the SCMBConnectionFailException.
        Test flow:
        """
        log = exceptions.SCMBConnectionFailException('Exception SCMBConnectionFailException raised')
        self.assertEqual(log.message, 'Exception SCMBConnectionFailException raised')

    def test_invalid_config_file(self):
        """Test case regarding the InvalidConfigFileException.
        Test flow:
        """
        log = exceptions.InvalidConfigFileException('Exception InvalidConfigFileException raised')
        self.assertEqual(log.message, 'Exception InvalidConfigFileException raised')
