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

"""Unit test cases for the manager_server_list.py module.
"""

from ovm_serverlist.model.node import Node
from ovm_serverlist.model.metric import Metric
from ovm_serverlist.manager.manager_oneview import ManagerOneView
from ovm_serverlist.manager.manager_server_list import ManagerServerList

from base import TestBase
from shared.config import ConfOneview

import os
import uuid
import mock


class TestManagerServerList(TestBase):
    """This class test the manager_ironic module from the ovm_serverlist.manager.
    """
    def setUp(self):
        """Setting up the tests.
        """
        super(TestManagerServerList, self).setUp()

        mac_file = '~' + os.path.sep + 'mac-file-test.yaml'
        self.mac_file = os.path.realpath(os.path.expanduser(mac_file))

        conf = ConfOneview()
        self.ov_manager = ManagerOneView(
            host=conf.host, username=conf.username, password=conf.password
        )

    def tearDown(self):
        """Tearing down the tests.
        """
        super(TestManagerServerList, self).tearDown()

    def test_reading_without_mac_file(self):
        """Test if the manager throws an exception when there is no mac file.
        Test flow:
                >>> Instanciate a new manager;
                >>> Try load a nonexistent mac file;
                >>> It ensures that an exception was thrown.
        """
        raised = False

        try:
            manager = ManagerServerList('~/false-mac-file.yaml', self.ov_manager)
            manager.load_mac_file()
        except Exception as ex:
            raised = True
            self.assertEqual(
                str(ex),
                '[Errno 2] No such file or directory: \'~/false-mac-file.yaml\''
            )

        self.assertTrue(raised)

    @mock.patch.object(ManagerOneView, 'get_server_hardware_uuid', return_value=None)
    def test_mac_file_empty(self, mock_get_sh_uuid):
        """Test if the manager work with existent, but empty mac file.
        Test flow:
                >>> Write a empty mac file;
                >>> Instanciate a new manager;
                >>> Run get_nodes_associated_oneview();
                >>> Verify if it returns an empty set.
        """
        with open(self.mac_file, 'w') as mac_file:
            mac_file.write('')
            mac_file.close()

        manager = ManagerServerList(self.mac_file, self.ov_manager)
        self.assertEqual(manager.get_nodes_associated_oneview(), set([]))

        os.remove(self.mac_file)

    @mock.patch.object(ManagerOneView, 'get_server_hardware_uuid')
    def test_manager_get_nodes_associated_oneview(self, mock_get_sh_uuid):
        """Test if the manager can process a mac file and returns
        the correct set of nodes.
        Test flow:
                >>> Write a mac file;
                >>> Instanciate a new manager;
                >>> Run get_nodes_associated_oneview();
                >>> Verify if it returns a correct set of nodes.
        """
        sh_mac, sh_uuid = '00:00:00:00:00:00', uuid.uuid4()

        # Writing in mac_file
        with open(self.mac_file, 'w') as mac_file:
            mac_file.write(
                'servers:\n' +
                '- mac-addr: ' + sh_mac +
                '\n  dimensions:\n       '
                'service: "compute"\n       hostname: "host_1"\n       cluster: 3'
            )
            mac_file.close()

        mock_get_sh_uuid.return_value = sh_uuid
        manager = ManagerServerList(self.mac_file, self.ov_manager)

        manager.load_mac_file()
        metric = Metric(
            'oneview.server_hardware',
            {'service': 'compute', 'hostname': 'host_1', 'cluster': '3',
             'server_hardware_uuid': sh_uuid}
        )

        expected_result = manager.get_nodes_associated_oneview()

        self.assertEqual(expected_result, {Node(sh_uuid, {metric})})
        os.remove(self.mac_file)
