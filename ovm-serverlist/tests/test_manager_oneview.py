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

from base import TestBase
from tests.shared.config import ConfOneview
from ovm_serverlist.shared.exceptions import LoginFailException
from ovm_serverlist.manager.manager_oneview import ManagerOneView

from hpOneView.exceptions import HPOneViewException
from hpOneView.resources.servers.server_hardware import ServerHardware

import mock
import uuid


class TestManagerOneview(TestBase):
    def setUp(self):
        super(TestManagerOneview, self).setUp()

        conf = ConfOneview()
        self.manager = ManagerOneView(
            host=conf.host, username=conf.username, password=conf.password
        )

    def tearDown(self):
        super(TestManagerOneview, self).tearDown()

    @mock.patch('hpOneView.connection.login')
    @mock.patch.object(ServerHardware, 'get_all')
    def test_get_server_hardware(self, mock_get_all, mock_login):
        sh_uuid1, sh_uuid2 = uuid.uuid4(), uuid.uuid4()
        mac1, mac2 = '11:11:11:11:11:11', '22:22:22:22:22:22'
        mock_get_all.return_value = [
            {"portMap": {
                "deviceSlots": [{
                    "physicalPorts": [{
                        "mac": mac1, "virtualPorts": []}]}]},
             "uuid": sh_uuid1},
            {"portMap": {
                "deviceSlots": [{
                    "physicalPorts": [{
                        "mac": "33:33:33:33:33:33", "virtualPorts": []}]}]},
             "uuid": uuid.uuid4()},
            {"portMap": {
                "deviceSlots": [{
                    "physicalPorts": [{
                        "mac": '00:00:00:00:00:00', "virtualPorts": [{"mac": mac2}]}]}]},
             "uuid": sh_uuid2},
        ]
        # test if return of manager is None
        expected_result = self.manager.get_server_hardware_uuid('44:44:44:44:44:44')
        self.assertIsNone(expected_result)
        # test if return of manager is the uuid of sh 1
        expected_result = self.manager.get_server_hardware_uuid(mac1)
        self.assertEquals(sh_uuid1, expected_result)
        # test if return of manager is the uuid of sh 2
        expected_result = self.manager.get_server_hardware_uuid(mac2)
        self.assertEquals(sh_uuid2, expected_result)

    @mock.patch('hpOneView.connection.login')
    @mock.patch.object(ServerHardware, 'get_all')
    def test_get_server_hardware_with_error(self, mock_get_all, mock_login):
        raised = False
        mac = '00:00:00:00:00:00'

        mock_get_all.return_value = []
        mock_login.side_effect = [
            HPOneViewException('Invalid username or password or directory.'),
            HPOneViewException('Something happening'),
            Exception
        ]
        try:
            self.manager.get_server_hardware_uuid(mac)
        except Exception as ex:
            raised = True
            self.assertIsInstance(ex, LoginFailException)

        self.assertTrue(raised)

        try:
            raised = False
            self.manager.get_server_hardware_uuid(mac)
        except Exception as ex:
            raised = True
            self.assertEqual(ex.message, 'Something happening')

        self.assertTrue(raised)

        try:
            raised = False
            self.manager.get_server_hardware_uuid(mac)
        except Exception as ex:
            raised = True
            self.assertNotIsInstance(ex, HPOneViewException)

        self.assertTrue(raised)
        mock_get_all.assert_not_called()
