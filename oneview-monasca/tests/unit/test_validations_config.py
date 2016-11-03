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

"""Tests for the Validation Package
"""

from oneview_client import exceptions
from oneview_client.client import BaseClient
from oneview_monasca.infrastructure import validations

from base import TestBase
from tests.shared.config import Conf
from tests.shared.config import ConfIronic
from tests.shared.config import ConfOneview

import os
import mock
import hashlib


class TestValidationsConfig(TestBase):
    """ Class that contains the Validation package unit tests
    """
    def setUp(self):
        """ Default set up method.
        """
        super(TestValidationsConfig, self).setUp()

    def tearDown(self):
        """ Default tear down method.
        """
        super(TestValidationsConfig, self).tearDown()

    # this function test if a given value is a integer
    def test_is_positive_integer(self):
        """Test cases regarding the flows of the is_positive_integer method of the validation config module
        Test flow:
                >>> Test if the method returns thue when given a integer in the correct format as its parameter;
        """

        # testing if the method return is correct
        self.assertTrue(validations._is_positive_int('10'))
        # testing if the method return is correct
        self.assertFalse(validations._is_positive_int('-10'))
        # testing if the method return is correct
        self.assertTrue(validations._is_positive_int('+10'))
        # testing if the method return is correct
        self.assertFalse(validations._is_url('4.5'))

    # this function tests if a given value is a url
    def test_is_url(self):
        """ Test cases regarding the flows of the is_url method of the validation config module
        Test flow:
                >>> Test if the method returns true when given a url in the correct format as its parameter;
        """

        # testing if the method return is correct
        self.assertTrue(validations._is_url('http://10.4.1.1:5000/v3'))
        # testing if the method return is correct
        self.assertFalse(validations._is_url('ssh://localhost/something'))
        # testing if the method return is correct
        self.assertTrue(validations._is_url('https://www.mytestdomain:5000/v2.0'))
        # testing if the method return is correct
        self.assertFalse(validations._is_url('2001:db8::1:1:1:1:1'))

    # this function tests if a given oneview credentials is valid
    @mock.patch("ironicclient.client.get_client")
    @mock.patch.object(BaseClient, '_authenticate')
    @mock.patch('monascaclient.ksclient.KSClient', new_callable=mock.PropertyMock)
    def test_validate_config(self, mock_ksclient, mock_login, mock_ironic_client):
        """Test cases regarding the validate_config method.
            Test flow:
                    >>> Mock the monasca client authenticate and oneview login
                    >>> Test if a exception is raised when the config_file is None
                    >>> Test if a valid config_file any exception is raised
        """
        raised = False
        config_file = Conf()

        mock_ksclient.return_value.monasca_url = config_file.openstack.auth_url
        mock_ksclient.return_value.token = hashlib.sha1(os.urandom(128)).hexdigest()

        try:
            validations.validate_config(None)
        except:
            raised = True

        self.assertTrue(raised)

        try:
            raised = False
            validations.validate_config(config_file)
        except:
            raised = True

        self.assertFalse(raised)
        self.assertEqual(mock_login.call_count, 1)

    @mock.patch.object(BaseClient, '_authenticate')
    def test_chk_oneview_credentials(self, mock_login):
        """Test cases regarding the flows of the chk_oneview_credentials of the validation config module
            Test flow:
                    >>> Mock oneview client login; and
                    >>> Test if the method not raised when given a valid oneview credentials as its parameter;
        """
        raised = False
        config = ConfOneview()
        try:
            validations._chk_oneview_credentials(config.manager_url, config.username, config.password)
        except:
            raised = True

        self.assertFalse(raised)
        mock_login.side_effect = exceptions.OneViewNotAuthorizedException()

        try:
            validations._chk_oneview_credentials(config.manager_url, config.username, config.password)
        except Exception as ex:
            raised = True
            self.assertIsInstance(ex, validations.InvalidConfigFileException)

        self.assertTrue(raised)

        raised = False
        try:
            validations._chk_oneview_credentials('test', 'test', 'test', 'test', 'test', 'test')
        except:
            raised = True

        self.assertTrue(raised)

    # this function tests if a given openstack credentials is valid
    @mock.patch("ironicclient.client.get_client")
    def test_chk_openstack_credentials(self, mock_ironic_client):
        """Test cases regarding the flows of the chk_openstack_credentials of the validation config module
            Test flow:
                    >>> Test if the method not raised when given a valid openstack credentials as its parameter;
        """
        raised = False
        config = ConfIronic()
        try:
            validations._chk_ironic_credentials(
                config.auth_url, config.admin_user, config.admin_password, config.admin_tenant_name, config.insecure,
                config.ironic_api_version
            )
        except:
            raised = True

        self.assertFalse(raised)
        mock_ironic_client.side_effect = Exception

        try:
            validations._chk_ironic_credentials(
                'http://127.0.0.1:5000/v2.0', 'user', 'password', 'project', 'true', '1.11'
            )
        except Exception as ex:
            raised = True
            mock_ironic_client.assert_called_with(
                1, insecure=True,
                os_auth_url='http://127.0.0.1:5000/v2.0',
                os_ironic_api_version='1.11',
                os_password='password',
                os_tenant_name='project',
                os_username='user'
            )
            self.assertIsInstance(ex, validations.InvalidConfigFileException)

        self.assertTrue(raised)
        self.assertEqual(mock_ironic_client.call_count, 2)
