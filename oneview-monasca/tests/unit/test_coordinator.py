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

""" This module represents the tests for Fault Tolerance Controller component from oneview_monasca agent."""

from base import TestBase
from tests.shared.config import ConfTooz

from oneview_monasca.application import coordinator

import mock


class TestCoordinator(TestBase):
    """ This class test the coordinator module from oneview_monasca.shared.
    """
    def setUp(self):
        """ Setting up the attributes shared between tests.
        """
        self.conf = ConfTooz()
        self.fake_callback = mock.Mock()
        super(TestCoordinator, self).setUp()

    def tearDown(self):
        """ Tearing down the attributes shared between tests.
        """
        super(TestCoordinator, self).tearDown()

    # Testing if objects created even using the same parameters are different
    def test_coordinators_not_equals_each_other(self):
        """ Test cases regarding the __init__ method of the Coordinator class
        Test flow:
                >>> Create two objects of the class;
                >>> Mock method _im_leader to avoid infinite loop in the test;
                >>> Test if an object is not equal to each other;
                >>> Test if an object is equal to itself;
        """
        daemon_coord = coordinator.Coordinator(self.conf, self.fake_callback)
        daemon_coord_2 = coordinator.Coordinator(self.conf, self.fake_callback)
        daemon_coord._im_leader = mock.Mock(return_value=True)
        daemon_coord_2._im_leader = mock.Mock(return_value=True)
        # testing if first and second objects are different
        self.assertNotEqual(daemon_coord, daemon_coord_2)
        # testing the first object is equal to himself
        self.assertEqual(daemon_coord, daemon_coord)
        # testing the second object is equal to himself
        self.assertEqual(daemon_coord_2, daemon_coord_2)

    # Testing attributes of different coordinators
    def test_coordinators_attributes(self):
        """ Test cases regarding the __init__ method of the Coordinator class
        Test flow:
                >>> Create two objects of the class;
                >>> Mock method _im_leader to avoid infinite loop in the test;
                >>> Test if an object id is equal to each other;
                >>> Test if the object group_name is equal to each other;
                >>> Test if the object coordinator_url is equal to each other;

                >>> Create an object of the class;
                >>> Test if the Coordinator constructor is called using the informations same informations of conf;
        """
        daemon_coord = coordinator.Coordinator(self.conf, self.fake_callback)
        daemon_coord_2 = coordinator.Coordinator(self.conf, self.fake_callback)
        daemon_coord._im_leader = mock.Mock(return_value=True)
        daemon_coord_2._im_leader = mock.Mock(return_value=True)
        # Test if the id are not equals for different objects
        self.assertNotEqual(daemon_coord._id, daemon_coord_2._id)
        # Test if the group_name is equal using the same configuration
        self.assertEqual(daemon_coord._group, daemon_coord_2._group)
        # Test if the backend url is equal using the same configuration
        self.assertEqual(daemon_coord._coordinator_url,
                         daemon_coord_2._coordinator_url)

    # Testing if the method get_coordinator from tooz is called once, guaranteeing that a single coordinator is called
    # when the constructor is invoked.
    @mock.patch('tooz.coordination.get_coordinator')
    def test_tooz_coordinator_instantiation(self, tooz_get_coordinator_mock):
        """ Test cases regarding the __init__ method of the Coordinator class
        Test flow:
                >>> Create an object of the class;
                >>> Test if the Coordinator constructor is called using the informations same informations of conf;
        """
        coord = coordinator.Coordinator(self.conf, self.fake_callback)
        # Test if the method was called once in this context
        tooz_get_coordinator_mock.assert_called_once_with(self.conf.coordinator_url, coord._id)

    # Testing if the private method join_group from coordinator is called once when start() is invoked. It guarantee
    # that the member join the group once and have no member duplicates in the group.
    @mock.patch('tooz.coordination.get_coordinator')
    def test_join_group_called_once(self, tooz_get_coordinator_mock):
        """ Test cases regarding the __join_group method of the Coordinator class
        Test flow:
                >>> Create an object of the class;
                >>> Mock method __im_leader to avoid infinite loop in the test;
                >>> Starts Coordinator;
                >>> Test if the method join_group was called once
        """
        coord = coordinator.Coordinator(self.conf, self.fake_callback)

        coord._stopped = True
        coord._im_leader = mock.Mock(return_value=True)
        # Mocking the method that will be tested
        coord._join_group = mock.Mock()
        coord.start()
        # Test if join_group was called once
        coord._join_group.assert_called_once_with()
        coord.stop()

    # Testing if one new thread is opened to run watchers
    @mock.patch('tooz.coordination.get_coordinator')
    def test_run_watchers_called_once(self, tooz_get_coordinator_mock):
        """ Test cases regarding the __run_watchers method of the Coordinator class
        Test flow:
                >>> Create an object of the class;
                >>> Mock method __im_leader to avoid infinite loop in the test;
                >>> Mock method thread.start_new_thread to test if it was called;
                >>> Starts Coordinator;
                >>> Test if the method start_new_thread was called once with run_watchers as a parameter;
        """
        coord = coordinator.Coordinator(self.conf, self.fake_callback)

        coord._im_leader = mock.Mock(return_value=True)
        # Mocking the new_thread method to test if run_watchers is called for it.
        coord._run_watchers = mock.Mock()
        coord.start()
        # Test if only one thread was opened and it callback run_watchers
        coord._run_watchers.assert_called_once_with()

    # Testing if the start() method from tooz.CoordinatorDriver object is called once for each Coordinator object. It
    # guarantee that only one CoordinatorDriver is started for each Coordinator.
    @mock.patch('tooz.coordination.get_coordinator')
    def test_coordinator_start_called_once(self, tooz_get_coordinator_mock):
        """ Test cases regarding the start method of the Coordinator class
        Test flow:
                >>> Create an object of the class;
                >>> Mock method __im_leader to avoid infinite loop in the test;
                >>> Mock method CoordinatorDriver.start to test if it was called after;
                >>> Starts Coordinator;
                >>> Test if the method start was called once;
        """
        coord = coordinator.Coordinator(self.conf, self.fake_callback)

        coord._stopped = True
        coord._im_leader = mock.Mock(return_value=True)
        # Mocking the method for the first coordinator
        coord._coordinator.start = mock.Mock()
        coord.start()
        # Testing if the method is called once coord
        coord._coordinator.start.assert_called_once_with()

    # Testing if the method generate_id is called once for each Coordinator object.
    @mock.patch('oneview_monasca.application.coordinator.Coordinator._generate_id')
    def test_generate_id_called_once(self, generate_id_mock):
        """ Test cases regarding the __generate_id method of the Coordinator class
        Test flow:
                >>> Mock method __generate_id to test if it was called after;
                >>> Instantiate Coordinator;
                >>> Test if __generate_id was called once.
                >>> Instantiate Coordinator;
                >>> Test if __generate_id was called once more.
        """
        coordinator.Coordinator(self.conf, self.fake_callback)
        # Test if the method was called once for coord
        generate_id_mock.assert_called_once_with()
        coordinator.Coordinator(self.conf, self.fake_callback)
        # Test if with a second objected created generate_id was called two times
        self.assertEqual(generate_id_mock.call_count, 2)

    # Testing if the method _watch_elected_once is called once for each Coordinator object.
    @mock.patch('tooz.coordination.get_coordinator')
    def test_coordinator_watch_elected_once(self, tooz_get_coordinator_mock):
        """ Test cases regarding the CoordinatorDriver.start() method of the Coordinator class
        Test flow:
                >>> Create an object of the class;
                >>> Mock method __im_leader to avoid infinite loop in the test;
                >>> Mock method __leader_elected_callback to test if it was called after;
                >>> Starts Coordinator;
                >>> Test if the method __leader_elected_callback was called once with group_name and an callback as
                parameters;
        """
        coord = coordinator.Coordinator(self.conf, self.fake_callback)

        coord._stopped = True
        coord._im_leader = mock.Mock(return_value=True)
        coord._leader_elected_callback = mock.Mock()
        coord._coordinator.watch_elected_as_leader = mock.Mock()
        coord.start()
        # Testing if _coordinator.watch_elected_as_leader was called once with group_name and callback as parameters
        coord._coordinator.\
            watch_elected_as_leader.assert_called_once_with(self.conf.group_name,
                                                            coord._leader_elected_callback)

    def test_im_leader(self):
        """ Test cases regarding the _im_leader method.
        Test flow:
            >>> Create an object of the class;
            >>> Calls the method; and;
            >>> Checks if its return is false.
        """
        coord = coordinator.Coordinator(self.conf, self.fake_callback)
        leader = coord._im_leader()
        self.assertFalse(leader)

    def test_join_group_callback(self):
        """ Test case regarding the callback of a group join.
        """
        coord = coordinator.Coordinator(self.conf, self.fake_callback)
        raises = False
        try:
            coord._join_group_callback(None)
        except:
            raises = True

        self.assertFalse(raises)

    def test_leader_elected_callback(self):
        """ Test case regarding the callback of a leader election receiving
        None as parameter.
        """
        coord = coordinator.Coordinator(self.conf, self.fake_callback)
        raises = False
        try:
            coord._leader_elected_callback(None)
        except:
            raises = True

        self.assertTrue(raises)

    def test_leave_group_callback(self):
        """ Test case regarding the callback of a group leave receiving
        None as parameter.
        """
        coord = coordinator.Coordinator(self.conf, self.fake_callback)
        raises = False
        try:
            coord._leave_group_callback(None)
        except:
            raises = True

        self.assertTrue(raises)

    def test_run_watchers(self):
        """ Test case regarding the _run_watchers method.
        """
        coord = coordinator.Coordinator(self.conf, self.fake_callback)
        raises = False
        try:
            coord._run_watchers()
        except:
            raises = True
        self.assertTrue(raises)
