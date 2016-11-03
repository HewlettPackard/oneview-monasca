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
Tests of AbstractManager module.
"""
from base import TestBase

from oneview_monasca.manager import abstract_manager_oneview


class FakeImplOne(abstract_manager_oneview.AbstractManagerOneView):
    """Fake class that has the DiscoveryNodeSUbscriber as superclass but does not implement
    its abstract methods.
    """
    pass


class FakeImplTwo(abstract_manager_oneview.AbstractManagerOneView):
    """Fake class that has the DiscoveryNodeSUbscriber as superclass and implement its
    abstract methods.
    """
    def get_server_hardware_status(self, uuid, status):
        """Calls the superclass method, has to raise an exception.
        """
        super(FakeImplTwo, self).get_server_hardware_status(None, None)

    def get_server_hardware(self, uuid):
        """ Get a instance of a server hardware from oneview.
        :param uuid: the id associated oneview server hardware resource.
        :return: a instance of a oneview server hardware resource.
        """
        super(FakeImplTwo, self).get_server_hardware(None)

    def get_server_hardware_alerts(self, resource_uri, status):
        """Get the alerts associated an Oneview resource when it is not OK.
        :param resource_uri: the oneview uri resource.
        :param status: the status associated with input resource.
        :return: a dict that contains all alerts associated with input resource.
        """
        super(FakeImplTwo, self).get_server_hardware_alerts(None, None)

    def get_certificates(self):
        """ Get a hpOneView SDK connection.
        :return: a connection to communicate with Oneview Rest API.
        """
        super(FakeImplTwo, self).get_certificates()

    def validate_certificates(self):
        """ Validate the current SCMB certificates, if not expired.
        """
        super(FakeImplTwo, self).validate_certificates()


class TestAbstractManager(TestBase):
    """ Class that contains the  unit tests for the abstract manager module
    """
    def setUp(self):
        """Setting up the tests.
        """
        super(TestAbstractManager, self).setUp()

    def tearDown(self):
        """Tearing down the tests.
        """
        super(TestAbstractManager, self).tearDown()

    def test_exceptions1(self):
        """Test cases regarding the creation of the two classes that implement
        the DiscoveryNodeSubscriber as superclass.
        Test flow:
            >>> Tries to create a FakeImplOne;
            >>> Checks if an exception was raised;
                >>> Tries to create a FakeImplTwo; and,
                >>> Checks if an exception was raised;
        """
        raises = False
        try:
            f = FakeImplOne()
        except:
            raises = True
        self.assertTrue(raises)

        raises = False
        try:
            f = FakeImplTwo()
        except:
            raises = True
        self.assertFalse(raises)
        self.assertEqual(f, f)

    def test_exceptions2(self):
        """Test cases regarding a class that implement the DiscoveryNodeSubscriber
        as superclass.
        Test flow:
                >>> Creates a FakeImplTwo;
                >>> Calls the abstract method; and,
                >>> Checks if exceptions were raised;
        """

        f = FakeImplTwo()

        raises = False
        try:
            f.get_server_hardware_status(None, None)
        except:
            raises = True
        self.assertTrue(raises)

        raises = False
        try:
            f.get_server_hardware(None)
        except:
            raises = True
        self.assertTrue(raises)

        raises = False
        try:
            f.get_server_hardware_alerts(None, None)
        except:
            raises = True
        self.assertTrue(raises)

        raises = False
        try:
            f.get_certificates()
        except:
            raises = True
        self.assertTrue(raises)

        raises = False
        try:
            f.validate_certificates()
        except:
            raises = True
        self.assertTrue(raises)
