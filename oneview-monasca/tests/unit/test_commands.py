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

"""Unit test cases for the commands.py module.
"""


from base import TestBase
from tests.shared.fake import FakeArgs

from oneview_monasca.infrastructure import commands

import os
import mock
import getpass


class TestCommands(TestBase):
    """This class test the pase_command module from oneview_monasca.shared.
    """
    def setUp(self):
        """Setting up the tests.
        """
        super(TestCommands, self).setUp()
        self.args = FakeArgs()

    def tearDown(self):
        """Tearing down the tests.
        """
        super(TestCommands, self).tearDown()

    @mock.patch.object(getpass, 'getpass')
    @mock.patch('oneview_monasca.shared.utils.get_input')
    def test_do_genconfig(self, mock_input, mock_password):
        """Test cases regarding the flows of the do_genconfig method of commands module
            Test flow:
                    >>> Mock the user input
                    >>> Test the mock calls and checks if the config_file is created
                    >>> Remove config_file and checks if its not exists in given args
        """
        cert_dir = os.path.expanduser('~')
        args_file = os.path.expanduser(self.args.config_file)

        user_input = [
            'y', '1', '1', '1', cert_dir, '1',  # Default session
            'http://localhost:5000/v2.0', 'user', 'project_name', '2_0',  # Openstack session
            'http://localhost/', 'admin', 'y', '20', cert_dir + os.path.sep + 'tls_cacert.pem',  # Oneview session
            'y', 'group', 'tooz://10.0.0.1:1',  # Tooz session
            args_file
        ]
        mock_input.side_effect = user_input
        mock_password.side_effect = ['password', 'password']

        with mock.patch('oneview_monasca.shared.utils.list_names_driver', return_value=[]):
            commands.do_genconfig(self.args)

        self.assertEqual(mock_input.call_count, len(user_input))
        self.assertEqual(mock_password.call_count, 2)

        self.assertTrue(os.path.exists(args_file))

        os.remove(args_file)
        self.assertFalse(os.path.exists(args_file))
