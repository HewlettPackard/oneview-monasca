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
The module of Tests for Utils package
"""

from base import TestBase
from tests.shared.fake import FakeExtension

from oneview_monasca.shared import utils
from oneview_monasca.shared import constants as const
from oneview_monasca.shared.exceptions import LoginFailException

import os
import abc
import mock


class TestUtils(TestBase):
    """ Class that contains the Utils package unit tests
    """
    def setUp(self):
        """ Default set up method.
        """
        super(TestUtils, self).setUp()

    def tearDown(self):
        """ Default tear down method.
        """
        super(TestUtils, self).tearDown()

    # this function tests the constant LOG
    def test_log(self):
        """ Test cases regarding the values of the constants from the utils module.
        """
        # testing if it is equals to it self
        self.assertEqual(utils.LOG, utils.LOG)
        # testing if it is not empty
        self.assertNotEqual(utils.LOG, '')
        # testing if it is not equals to aleatory string
        self.assertNotEqual(utils.LOG, 'test')
        # testing if it is not null
        self.assertNotEqual(utils.LOG, None)

    # this function tests the extract_domain_from_service_url method
    def test_extract_domain_from_service_url(self):
        """ Test cases regarding the flows of the extract_domain_from_service_url method of the utils module
        Test flow:
                >>> test if the method returns the correct domain given a url in the correct format as its parameter;
                >>> test if the method does not return some alleatory string given a url in the correct format as
                its parameter; and,
                >>> test if the method raises an exception when it receives a url in the wrong format as its parameter.
        """
        # testing if the method return is correct
        self.assertEqual(utils.extract_domain_from_service_url('http://10.4.1.1:5000/v3'), '10.4.1.1')
        # testing if the method return is correct
        self.assertNotEqual(utils.extract_domain_from_service_url('http://10.4.1.1:5000/v3'), 'something')
        # testing if the method return is correct
        self.assertEqual(utils.extract_domain_from_service_url('http://10.4.1.1:5000/v3'), '10.4.1.1')
        # testing if the method return is correct
        self.assertNotEqual(utils.extract_domain_from_service_url('http://10.4.1.1:5000/v3'), 'something')
        # testing if an exception is raised when the parameter does not follow the expected format
        raised = False
        try:
            utils.extract_domain_from_service_url('something')
        except:
            raised = True
        self.assertTrue(raised)

    # this function tests the parse_timestamp method
    def test_parse_timestamp(self):
        """ Test cases regarding the flows of the parse_timestamp method of the utils module
        Test flow:
                >>> creates the variables to be used as the method parameters;
                >>> creates the expected result for the method execution when receiving the variable time1 as
                its parameter;
                >>> test if the result of the method execution when receving the variable time1 as its parameter is
                equal to the expected value;
                >>> test if the result of the method execution when receving the variable time2 as its parameter is
                different of the expected value when it receives the variable time1 as its parameter; and,
                >>> test if the method raises an exception when it receives a parameter in the wrong format.
        """
        # creating variables to use as parameters of the method
        time1 = '2014-08-07T11:00:11.467Z'
        time2 = '2014-08-07T20:56:35.467Z'
        # variable representing the expected value of the method execution with time1 as its parameter
        expected_result = 1407409211467
        # testing if method returns the correct value
        result = utils.parse_timestamp(time1)
        self.assertEqual(result, expected_result)
        # testing if method returns is different for a different timestamp
        result2 = utils.parse_timestamp(time2)
        self.assertNotEqual(result2, expected_result)
        # testing if an exception is raised when the parameter does not follow the expected format
        raised = False
        try:
            utils.parse_timestamp('2016-07-20 12:00:00')
        except:
            raised = True
        self.assertTrue(raised)

    # this function tests the list_names_driver method
    @mock.patch('stevedore.extension.ExtensionManager._load_plugins')
    def tests_list_names_driver(self, mock_extension):
        """ Test cases regarding the flows of the list_names_driver method of the utils module
        Test flow:
                >>> test if the method returns an empty list when the string received as parameter does not
                correspond to a namespace; and,
                >>> test if the method does not return an empty list when the string received as parameter correspond
                to a namespace.
        """
        mock_extension.side_effect = [[], [FakeExtension('ovm_ironic')]]

        # testing empty namespace
        self.assertEqual(utils.list_names_driver('monasca'), [])
        # testing existing namespace
        self.assertNotEqual(utils.list_names_driver('ovm_ironic'), [])

        raises = False
        try:
            utils.list_names_driver('test-namespace')
        except:
            raises = True
        self.assertTrue(raises)

    # this function test the try_execute method
    def test_try_execute(self):
        """ Test cases regarding the flows of the try_execute method of the utils module
            Test flow:
                    >>> create a empty array and execute a auxiliary function to appends n elements inside it.
                    >>> test if the method does not return an empty list an length of array is equal max_retry_attempts.
        """
        element, array = 10, []

        try:
            utils.try_execute(self.n_appends, 5, 0, element, array)
        except Exception as ex:
            self.assertEqual(array, [10, 10, 10, 10, 10])
            self.assertTrue(utils.not_retry_if_login_fail(ex))

    # this function test the try_execute method when is raise a instance of LoginFailException
    def test_try_execute_when_login_fail(self):
        """ Test cases regarding the flows of the try_execute method of the utils module
            Test flow:
                    >>> create a array that contains n elements
                    >>> test if the method does return an array contains n-1 elements when is raise a instance of
                    LoginFailException.
        """
        array = [10, 10, 10, 10, 10]

        try:
            utils.try_execute(self.n_pops, 5, 0, array)
        except LoginFailException as ex:
            self.assertEqual(array, [10, 10, 10, 10])
            self.assertFalse(utils.not_retry_if_login_fail(ex))

    @staticmethod
    def n_appends(element, array):
        """ Auxiliary function to test a retry decorator

        :param element: same element to append into array
        :param array: same array to appends elements
        :raises: a instance of Exception
        """
        array.append(element)
        raise Exception

    @staticmethod
    def n_pops(array):
        """ Auxiliary function to test a retry decorator

        :param array: same array to pop elements
        :raises: a instance of LoginFailException
        """
        array.pop()
        raise LoginFailException

    def test_makedirs(self):
        """Test case regarding the creation of a dir based on a given/desired path.
           Test flow:
                   >>> Stores the desired path in dir_name variable;
                   >>> Stores the complete full path in full_dir_name variable;
                   >>> Calls the method to create dir_name;
                   >>> Checks if the dir exists;
                   >>> Deletes the dir;
                   >>> Checks if the dir does not exists;
                   >>> Tries to call the method with an invalid path; and,
                   >>> Checks if an exception occurred.
        """
        dir_name = 'test-monasca-000'
        full_dir_name = os.path.expanduser('~') + os.path.sep + dir_name

        utils.makedirs(dir_name)
        self.assertTrue(os.path.exists(full_dir_name))
        os.rmdir(full_dir_name)
        self.assertFalse(os.path.exists(full_dir_name))

        raises = False
        try:
            utils.makedirs(None)
        except:
            raises = True

        self.assertTrue(raises)

    def test_save_file(self):
        """Test case regarding the creation of a dir based on a given/desired path.
           Test flow:
                   >>> Stores the dir name in dir_name variable;
                   >>> Stores the complete full path in full_dir_name variable;
                   >>> Stores the file name in file_name variable;
                   >>> Calls the method to save the file and stores the file path in path_file variable;
                   >>> Checks if the file exists;
                   >>> Deletes the dir; and,
                   >>> Checks if the dir does not exists.
        """
        dir_name = 'test-monasca-000'
        full_dir_name = os.path.expanduser('~') + os.path.sep + dir_name

        file_name = 'test_file.txt'
        path_file = utils.save_file(full_dir_name, file_name, "certificate")

        self.assertTrue(os.path.isfile(path_file))
        os.rmdir(full_dir_name)
        self.assertFalse(os.path.exists(full_dir_name))

    def test_extract_oneview_uuid(self):
        """Test case regarding the extraction of the oneview_uuid from an oneview_uri.
           Test flow:
                >>> Stores an oneview_uuid;
                >>> Uses the stored oneview_uuid to build an oneview_uri;
                >>> Calls the method with oneview_uri as parameter; and,
                >>> Checks if the method return is equal to the stored oneview_uuid.
        """
        server_hardware_uuid = '123-abc'
        oneview_uri = const.ONEVIEW_URI_PREFIX + server_hardware_uuid

        ov_uuid = utils.extract_oneview_uuid(oneview_uri)

        self.assertEqual(ov_uuid, server_hardware_uuid)

    def test_load_class_by_alias(self):
        """Test case regarding the load of a class by alias.
        Test flow:
                >>> Calls the list_names_driver method to get the drivers of a given namespace;
                >>> For each driver, calls the method;
                >>> Checks if the loaded class has the type abc.ABCMeta.
                >>> Tries to call the method with None parameters; and,
                >>> Checks if an exception was raised.
        """
        names = utils.list_names_driver(const.NAMESPACE_DISCOVERY_NODES)
        for name in names:
            class_ = utils.load_class_by_alias(const.NAMESPACE_DISCOVERY_NODES, name)
            self.assertEqual(type(class_), abc.ABCMeta)

        raises = False
        try:
            utils.load_class_by_alias(None, None)
        except:
            raises = True
        self.assertTrue(raises)

        raises = False
        try:
            utils.load_class_by_alias('test-namespace', 'test-name')
        except:
            raises = True
        self.assertTrue(raises)
