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
Class to test the Manager OneView behavior.
"""

from base import TestBase
from oneview_monasca.manager.manager_oneview import ManagerOneView
from oneview_monasca.shared.exceptions import LoginFailException
from oneview_monasca.shared import constants as const
from tests.shared.fake import FakeManagerOneview
from tests.shared.config import Default
from tests.shared.config import ConfOneview

from hpOneView import activity
from hpOneView import security
from hpOneView import connection
from hpOneView.exceptions import HPOneViewException
from hpOneView.oneview_client import ServerHardware

import os
import uuid
import mock


class TestManagerOneview(TestBase):
    """ Class that contains the Manager OneView unit tests
    """
    def setUp(self):
        """ Set up the same managers that will be used into the tests cases.
        """
        super(TestManagerOneview, self).setUp()

        default = Default()
        conf = ConfOneview()

        self.fake_manager = FakeManagerOneview()
        self.manager = ManagerOneView(
            conf.host, conf.username, conf.password, conf.max_attempt, default.scmb_certificate_dir
        )

    def tearDown(self):
        """ Default tear down method.
        """
        super(TestManagerOneview, self).tearDown()

    @mock.patch.object(connection, 'login')
    @mock.patch.object(ServerHardware, 'get')
    def test_get_server_hardware(self, mock_client, mock_login):
        """ Test cases regarding the flows of the get_server_hardware method of Manager Oneview module
            Test flow:
                    >>> Try get server hardware instance with a manager that contains wrongs parameters.
                    >>> test if the method does try execute the method action and the correct exception is raised.
        """
        raised, sh_uuid = False, uuid.uuid4()
        mock_login.side_effect = [
            HPOneViewException({'message': const.LOGIN_FAILED}), HPOneViewException('Connection refused')
        ]

        try:
            self.manager.get_server_hardware(sh_uuid)
        except LoginFailException as ex:
            raised = True
            self.assertIsInstance(ex, LoginFailException)
            self.assertEqual(ex.message, const.LOGIN_FAILED)
        finally:
            self.assertTrue(raised)
        try:
            raised = False
            self.manager.get_server_hardware(sh_uuid)
        except HPOneViewException as ex:
            raised = True
            self.assertIn('Connection refused', ex.msg)
        finally:
            self.assertTrue(raised)
            self.assertEqual(mock_login.call_count, 2)

            conf = ConfOneview()
            mock_login.assert_called_with({'userName': conf.username, 'password': conf.password})

        mock_login.side_effect = None
        mock_client.return_value = self.fake_manager.get_server_hardware(sh_uuid)

        result = self.manager.get_server_hardware(sh_uuid)
        expected_result = self.fake_manager.get_server_hardware(sh_uuid)

        mock_client.assert_called_with(sh_uuid)
        self.assertEqual(result, expected_result)

    @mock.patch.object(ManagerOneView, 'get_server_hardware')
    def test_get_server_hardware_status(self, mock_manager):
        """ Test cases regarding the flows of the get_server_hardware_status method of Manager Oneview module
            Test flow:
                    >>> Mock two expected results to get server hardware status
                    >>> Test if the call method result is equal of the expected results
                    >>> Test if the get_server_hardware_status method is twice calling only
        """
        sh_status, sh_uuid = 'OK', uuid.uuid4()

        expected_result1 = self.fake_manager.get_server_hardware_status()
        expected_result2 = self.fake_manager.get_server_hardware_status(sh_status)

        mock_manager.side_effect = [expected_result1, expected_result2]

        status = self.manager.get_server_hardware_status(sh_uuid, sh_status)

        self.assertEqual(status, 0)
        self.manager.get_server_hardware.assert_not_called()

        status, timestamp = self.manager.get_server_hardware_status(sh_uuid)

        self.assertEqual(status, 3)
        self.assertEqual(timestamp, '2014-08-07T11:00:11.467Z')
        self.manager.get_server_hardware.assert_called_with(sh_uuid)

        self.assertEqual(mock_manager.call_count, 1)

    @mock.patch.object(activity, 'get_alerts')
    @mock.patch.object(ManagerOneView, 'get_connection')
    def test_get_server_hardware_alerts(self, mock_manager, mock_get_alerts):
        """
        Test cases regarding the test_get_server_hardware_alerts method.
        :param mock_manager: a mocked manager
        :param mock_get_alerts: the mocked method get_alerts
        """
        sh_uuid = str(uuid.uuid4())

        mock_manager.return_value = None
        mock_get_alerts.return_value = self.fake_manager.get_server_hardware_alerts(sh_uuid)

        result = self.manager.get_server_hardware_alerts(sh_uuid, 0)

        self.assertEqual(result, dict())
        self.manager.get_connection.assert_not_called()

        result = self.manager.get_server_hardware_alerts(sh_uuid, 3)

        key = '/server-hardware/' + sh_uuid
        value = self.manager._host + '#/activity/r' + key

        self.assertEqual(result, {key: value})
        self.assertEqual(mock_get_alerts.call_count, 1)
        self.manager.get_connection.assert_called_with()

    @mock.patch.object(connection, 'login')
    def test_get_connection(self, mock_login):
        """ Test cases regarding the flows of the get_connection method of Manager Oneview module
            Test flow:
                    >>> Try create a connection with a manager that contains wrongs parameters.
                    >>> test if the method does try execute the method action and the correct exception is raised.
        """
        raised = False
        mock_login.side_effect = [
            HPOneViewException({'message': const.LOGIN_FAILED}), HPOneViewException('Connection refused')
        ]

        try:
            self.manager.get_connection()
        except LoginFailException as ex:
            raised = True
            self.assertIsInstance(ex, LoginFailException)
            self.assertEqual(ex.message, const.LOGIN_FAILED)
        finally:
            self.assertTrue(raised)

        try:
            raised = False
            self.manager.get_connection()
        except Exception as ex:
            raised = True
            self.assertIn('Connection refused', ex.args)
        finally:
            self.assertTrue(raised)

        mock_login.side_effect = None
        with mock.patch.object(connection, 'get_eula_status') as mock_eula:
            mock_eula.return_value = False
            con = self.manager.get_connection()

        self.assertIsInstance(con, connection)
        self.assertEqual(mock_login.call_count, 3)

    @mock.patch.object(connection, 'login')
    @mock.patch.object(security, 'get_cert_ca')
    @mock.patch.object(security, 'get_rabbitmq_kp')
    def test_get_certificates(self, mock_rabbitmq_kq, mock_get_cert_ca, mock_login):
        """Test cases regarding the flows of the get_certificates of Manager Oneview module
           Test flow:
                   >>> Mock the expected result to get server scmb certificates
                   >>> Test if the call method result is equal of the expected result
                   >>> Test if the get_certificates method is once calling only
        """
        mock_login.return_value = None
        mock_get_cert_ca.return_value = 'I am is a fake ca certificate'
        mock_rabbitmq_kq.return_value = {
            'base64SSLKeyData': 'I am is a fake key certificate',
            'base64SSLCertData': 'I am is a fake client certificate'
        }
        with mock.patch.object(connection, 'get_eula_status') as mock_eula:
            mock_eula.return_value = False
            self.manager.get_certificates()

        default = Default()
        conf = ConfOneview()

        mock_login.assert_called_once_with({'userName': conf.username, 'password': conf.password})

        self.assertEqual(mock_get_cert_ca.call_count, 1)
        self.assertEqual(mock_rabbitmq_kq.call_count, 1)

        self.assertTrue(os.path.exists(default.scmb_certificate_dir + '/key.pem'))
        self.assertTrue(os.path.exists(default.scmb_certificate_dir + '/caroot.pem'))
        self.assertTrue(os.path.exists(default.scmb_certificate_dir + '/client.pem'))

        os.remove(default.scmb_certificate_dir + '/key.pem')
        os.remove(default.scmb_certificate_dir + '/caroot.pem')
        os.remove(default.scmb_certificate_dir + '/client.pem')

        self.assertFalse(os.path.exists(default.scmb_certificate_dir + '/key.pem'))
        self.assertFalse(os.path.exists(default.scmb_certificate_dir + '/caroot.pem'))
        self.assertFalse(os.path.exists(default.scmb_certificate_dir + '/client.pem'))

    @mock.patch.object(connection, 'login')
    @mock.patch.object(security, 'gen_rabbitmq_self_signed_ca')
    def test_validate_certificates(self, mock_validate_cert, mock_login):
        """Test cases regarding the flows of the validate_certificates of Manager Oneview module
           Test flow:
                   >>> Mock the expected result to validate certificates
                   >>> Test if the call method result is equal of the expected result
        """
        with mock.patch.object(connection, 'get_eula_status') as mock_eula:
            mock_login.return_value = None
            mock_eula.return_value = False
            self.manager.validate_certificates()

            self.assertEqual(mock_validate_cert.call_count, 1)

            raised = False
            mock_validate_cert.side_effect = [Exception(const.CERTIFICATE_VALID), Exception('Something happened')]

            try:
                self.manager.validate_certificates()
            except Exception:
                raised = True
            finally:
                self.assertFalse(raised)
                self.assertEqual(mock_validate_cert.call_count, 2)

            try:
                self.manager.validate_certificates()
            except Exception as ex:
                raised = True
                self.assertEqual(ex.message, 'Something happened')
            finally:
                self.assertTrue(raised)
                self.assertEqual(mock_validate_cert.call_count, 3)
