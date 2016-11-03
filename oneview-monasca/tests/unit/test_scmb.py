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

""" This test module cover the SCMB module.
"""

from oneview_monasca.shared import utils
from pika.adapters import blocking_connection
from oneview_monasca.publisher.scmb import SCMB
from oneview_monasca.model.status import Status
from oneview_monasca.shared.exceptions import LoginFailException
from oneview_monasca.manager.manager_oneview import ManagerOneView
from oneview_monasca.shared.exceptions import SCMBConnectionFailException

from base import TestBase
from tests.shared.node import Node
from tests.shared.metric import Metric
from tests.shared.fake import FakeKeeper
from tests.shared.config import Default
from tests.shared.config import ConfOneview
from tests.shared.fake import FakeSelectConnection

import mock
import uuid


class TestSCMB(TestBase):
    """
    This class test SCMB module.
    """
    def setUp(self):
        """
        Setting up the variables.
        Creating an object Keeper.
        """
        super(TestSCMB, self).setUp()
        default = Default()
        self.conf = ConfOneview()

        self.manager = ManagerOneView(
            self.conf.host,
            self.conf.username,
            self.conf.password,
            self.conf.max_attempt, default.scmb_certificate_dir
        )
        self.scmb = SCMB(self.manager, self.conf.host, 2, None)

    def tearDown(self):
        """
        Tearing down the objects.
        """
        super(TestSCMB, self).tearDown()

    @staticmethod
    def create_fake_node_plugin(server_hardware_uuid, service, len_metrics=1):
        """ Method that create a fake node to be used into tests.

        :param server_hardware_uuid: String. Fake Server Hardware uuid.
        :param service: String to indicate the service.
        :param len_metrics: Integer to set up the length of the set of metrics.
        """
        metric_name = 'oneview.server_hardware'
        metrics = set()
        for i in range(len_metrics):
            dimensions = {'service': service}
            if len_metrics > 1:
                dimensions['something-dimension'] = i
            metrics.add(Metric(metric_name, dimensions))

        return Node(server_hardware_uuid, metrics)

    @mock.patch.object(ManagerOneView, 'get_certificates')
    def test_scmb_broken_initialize(self, mock_get_certificates):
        """Test the creation of the SCMB.
        """
        raised = False
        self.scmb._crash_callback = mock.MagicMock(
            name='mock_crash_callback',
            side_effect=[
                LoginFailException('Login Fail'),
                SCMBConnectionFailException('Something happening with SCMB connection')
            ]
        )
        mock_get_certificates.side_effect = [LoginFailException('Login Fail'), {}, {}, {}]

        # Set a fake starting to Thread
        self.scmb._stopped = False

        try:
            self.scmb.run()
        except Exception as ex:
            raised = True
            self.assertIsInstance(ex, LoginFailException)
            self.assertEqual(ex.message, 'Login Fail')
        finally:
            self.assertTrue(raised)
            raised = False
        try:
            self.scmb.run()
        except Exception as ex:
            raised = True
            self.assertIsInstance(ex, SCMBConnectionFailException)
            self.assertEqual(ex.message, 'Something happening with SCMB connection')
        finally:
            self.assertTrue(raised)

        self.assertFalse(self.scmb.isAlive())

    def test_available(self):
        """Test the available method.
        """
        node = self.create_fake_node_plugin('server_hardware_uuid2', 'ironic')

        self.scmb.available({node})
        self.assertEqual(len(self.scmb._monitored_nodes), 1)

    def test_unavailable(self):
        """Test the unavailable method
        """
        node = self.create_fake_node_plugin('server_hardware_uuid2', 'ironic')

        self.scmb.available({node})
        self.assertEqual(len(self.scmb._monitored_nodes), 1)

        node.metrics.clear()
        self.scmb.unavailable({node})
        self.assertEqual(len(self.scmb._monitored_nodes), 0)

    @mock.patch.object(ManagerOneView, 'get_server_hardware_status')
    def test_get_status(self, mock_manager):
        """Test the get_status method
        """
        status_ok = 0
        status_wa = 3
        str_timestamp = '2014-08-07T11:00:11.467Z'
        timestamp = utils.parse_timestamp(str_timestamp)

        resource = uuid.uuid4()
        mock_manager.side_effect = [status_wa, status_ok, Exception]

        status_obj = self.scmb._get_status(resource, 'Warning', str_timestamp)
        self.assertEqual(status_obj, Status(resource, status_wa, timestamp))

        status_obj = self.scmb._get_status(resource, 'OK', str_timestamp)
        self.assertEqual(status_obj, Status(resource, status_ok, timestamp))

        self.scmb._crash_callback = mock.MagicMock(
            name='mock_crash_callback',
            side_effect=Exception('Something happening with OneView Manager')
        )
        try:
            self.scmb._get_status(resource, 'OK', str_timestamp)
        except Exception as ex:
            self.assertEqual(ex.message, 'Something happening with OneView Manager')

        self.assertEqual(mock_manager.call_count, 3)

    @mock.patch('json.loads')
    @mock.patch.object(ManagerOneView, 'get_server_hardware_status')
    def test_scmb_callback(self, mock_manager, mock_json_loads):
        """Test the scmb_callback method
        """
        subscriber = FakeKeeper()
        self.scmb.subscribe(subscriber)

        resource = uuid.uuid4()
        mock_manager.return_value = 0

        mock_json_loads.return_value = {
            'resource': {'uuid': resource, 'status': 'OK', 'modified': '2014-08-07T11:00:11.467Z'}
        }
        self.scmb._scmb_callback(None, mock.MagicMock(), None, mock_json_loads)
        self.assertEqual(len(subscriber.states), 0)

        node = self.create_fake_node_plugin(resource, 'test_scmb', 2)
        self.scmb.available({node})

        self.scmb._scmb_callback(None, mock.MagicMock(), None, mock_json_loads)
        self.assertEqual(len(subscriber.states), 1)

        status_obj = Status(resource, 0, utils.parse_timestamp('2014-08-07T11:00:11.467Z'))
        self.assertTrue(status_obj in subscriber.states)

    @mock.patch.object(ManagerOneView, 'get_certificates')
    @mock.patch.object(ManagerOneView, 'validate_certificates')
    @mock.patch('pika.adapters.blocking_connection.BlockingConnection.close')
    @mock.patch.object(blocking_connection, 'SelectConnection', spec_set=FakeSelectConnection)
    def test_connection(self, mock_connection, mock_close, mock_valid_cert, mock_certificates):
        """Test the connection method
        """
        mock_certificates.return_value = None
        with mock.patch.object(blocking_connection.BlockingConnection, '_process_io_for_connection_setup'):
            conn = self.scmb.connection

        self.assertTrue(conn.is_open)
        self.assertEqual(mock_connection.call_count, 1)

        self.scmb.connection = None
        self.assertIsNone(self.scmb._connection)
