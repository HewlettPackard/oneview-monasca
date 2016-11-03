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

"""Unit test cases for the manager_monasca.py module.
"""

from oneview_monasca.model.measurement import Measurement
from oneview_monasca.manager.manager_monasca import ManagerMonasca

from base import TestBase
from tests.shared.config import ConfOpenstack

import os
import mock
import hashlib


@mock.patch('monascaclient.ksclient.KSClient', new_callable=mock.PropertyMock)
class TestManagerMonasca(TestBase):
    """ Class that contains the Manager OneView unit tests
    """

    def setUp(self):
        """ Set up the same managers that will be used into the tests cases.
        """
        super(TestManagerMonasca, self).setUp()

        conf = ConfOpenstack()
        self.manager = ManagerMonasca(
            conf.auth_url, conf.auth_user, conf.auth_password, conf.auth_tenant_name, conf.monasca_api_version
        )

        self.endpoint_url = 'http://127.0.0.1:8070/v2.0'
        self.token = hashlib.sha1(os.urandom(128)).hexdigest()

    def tearDown(self):
        """ Default tear down method.
        """
        super(TestManagerMonasca, self).tearDown()

    def test_get_monasca_client(self, mock_ksclient):
        """ Test cases regarding the flows of the get_monasca_client method of Manager Oneview module
            Test flow:
                    >>> Mock the keystone client
                    >>> Get a instance of Monasca client by Manager Monasca
                    >>> Test if the instance client has a fake token and endpoint_url that belongs to mock ksclient
        """
        mock_ksclient.return_value.monasca_url = self.endpoint_url
        mock_ksclient.return_value.token = self.token

        monclient = self.manager._get_monasca_client()
        self.assertEqual(self.token, monclient.http_client.auth_token)
        self.assertEqual(self.endpoint_url, monclient.http_client.endpoint_url)

    @mock.patch('monascaclient.common.http.HTTPClient.json_request')
    def test_send_metrics(self, mock_httpclient, mock_ksclient):
        """ Test cases regarding the flows of the send_metrics method of Manager Oneview module
        """
        mock_ksclient.return_value.monasca_url = self.endpoint_url
        mock_ksclient.return_value.token = self.token
        mock_httpclient.return_value = 200, {}

        raised = False
        measure = Measurement(name='oneview.testMetric', value=0, dimensions={'service': 'test'}, value_meta={})
        metric = {
            'name': measure.name, 'value': measure.value, 'timestamp': measure.timestamp,
            'dimensions': measure.dimensions, 'value_meta': measure.value_meta
        }
        try:
            self.manager.send_metrics([measure])
        except:
            raised = True

        self.assertFalse(raised)
        mock_httpclient.assert_called_once_with('POST', '/metrics', data=[metric], headers={})

        mock_httpclient.side_effect = Exception('Something happened')
        try:
            self.manager.send_metrics([measure])
        except Exception as ex:
            raised = True
            self.assertEqual(ex.message, 'Something happened')

        self.assertTrue(raised)
