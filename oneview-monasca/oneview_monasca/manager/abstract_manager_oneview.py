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
This module provide an Abstract Manager OneView that is a interface to create a
channel between the OneView Rest API and the publishers.
"""

import abc
import six


@six.add_metaclass(abc.ABCMeta)
class AbstractManagerOneView(object):
    """ Interface of a Manager OneView object.
    """
    @abc.abstractmethod
    def get_server_hardware_status(self, uuid, status):
        """ Get server hardware status and returns.

            :param uuid: The uuid of an specific server hardware.
            :param status: The current status associated an specific server hardware.

            :returns The status of corresponding server hardware.

        """
        raise NotImplementedError("Method not implemented, subclasses should implement this!")

    @abc.abstractmethod
    def get_server_hardware(self, uuid):
        """ Get a instance of a server hardware from oneview.

            :param uuid: the id associated oneview server hardware resource.
            :return: a instance of a oneview server hardware resource.
        """
        raise NotImplementedError("Method not implemented, subclasses should implement this!")

    @abc.abstractmethod
    def get_server_hardware_alerts(self, resource_uri, status):
        """Get the alerts associated an Oneview resource when it is not OK.

            :param resource_uri: the oneview uri resource.
            :param status: the status associated with input resource.

            :return: a dict that contains all alerts associated with input resource.
        """
        raise NotImplementedError("Method not implemented, subclasses should implement this!")

    @abc.abstractmethod
    def get_certificates(self):
        """ Get a hpOneView SDK connection.

            :return: a connection to communicate with Oneview Rest API.
        """
        raise NotImplementedError("Method not implemented, subclasses should implement this!")

    @abc.abstractmethod
    def validate_certificates(self):
        """ Validate the current SCMB certificates, if not expired.

        """
        raise NotImplementedError("Method not implemented, subclasses should implement this!")
