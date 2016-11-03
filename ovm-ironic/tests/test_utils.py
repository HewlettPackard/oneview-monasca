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
Unit tests for the Utils module.
"""
from base import TestBase
from ovm_ironic.shared.exceptions import LoginFailException
from ovm_ironic.shared import utils


class TestUtils(TestBase):
    """ This class test the utils module from oneview_monasca.shared.
    """
    def setUp(self):
        super(TestUtils, self).setUp()
        self.namespace = 'node_discovery.driver'
        self.alias = 'ovm_ironic'

    def tearDown(self):
        super(TestUtils, self).tearDown()

    def test_load_class_by_alias(self):
        """Test cases regarding the load_class_by_alias method of the Utils module
        Test flow:
                >>> Checks if an ImportError exception is raised when the wrong
                alias is received by the load_class_by_alias method.
        """
        with self.assertRaises(ImportError) as ctx:
            utils.load_class_by_alias(self.namespace, 'wrong_alias')

        self.assertIn('Class not found.', ctx.exception)

    def test_extract_oneview_uuid(self):
        """Test cases regarding the extract_oneview_uuid method of the Utils module.
        """
        self.assertEquals(utils.extract_oneview_uuid("/server-hardware/uuid"), "uuid")

    # this function test the try_execute method
    def test_try_execute(self):
        """ Test cases regarding the flows of the try_execute method of the utils module
            Test flow:
                    >>> create a empty array and execute a auxiliary function to
                    appends n elements inside it.
                    >>> test if the method does not return an empty list an length of array
                    is equal max_retry_attempts.
        """
        element, array = 10, []

        try:
            utils.try_execute(self.n_appends, 2, 0, element, array)
        except Exception as ex:
            self.assertEqual(array, [10, 10])
            self.assertTrue(utils.not_retry_if_login_fail(ex))

    # this function test the try_execute method when is raise a instance of LoginFailException
    def test_try_execute_when_login_fail(self):
        """ Test cases regarding the flows of the try_execute method of the utils module
            Test flow:
                    >>> create a array that contains n elements
                    >>> test if the method does return an array contains n-1 elements when
                    is raise a instance of LoginFailException.
        """
        array = [10, 10]

        try:
            utils.try_execute(self.n_pops, 2, 0, array)
        except LoginFailException as ex:
            self.assertEqual(array, [10])
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
        raise LoginFailException()
