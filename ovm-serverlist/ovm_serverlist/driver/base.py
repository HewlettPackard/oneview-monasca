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
Provides the discovery node services.
"""

from abc import abstractmethod
from ovm_serverlist.shared import utils as utils
from ovm_serverlist.shared import log as logging

import os
import abc
import six

LOG = logging.get_logger(__name__)


@six.add_metaclass(abc.ABCMeta)
class DiscoveryNodeProvider(object):
    """
    This class should be implemented by providers.
    """
    def __init__(self, debug=False):
        self.debug = debug
        self.subscribers = {}

    def subscribe(self, subscriber):
        """Subscribe a listener.

        :param subscriber: the listener component.
        """
        key = subscriber.__class__.__name__
        if key not in self.subscribers.keys():
            utils.print_log_message('Info', 'Subscribe: %s' % key, LOG)
            self.subscribers[key] = subscriber

    def unsubscribe(self, subscriber):
        """Unsubscribe a listener

        :param subscriber: the listener component.
        """
        key = subscriber.__class__.__name__
        if key in self.subscribers.keys():
            utils.print_log_message('Info', 'Unsubscribe: %s' % key, LOG)
            del self.subscribers[key]

    def available(self, nodes):
        """Turns nodes available.

        :param nodes: nodes collection to be available.
        """
        for subscriber in self.subscribers.values():
            message = "Registering nodes %(nodes)s in subscriber %(subscriber)s" % {
                "nodes": nodes, "subscriber": subscriber.__class__.__name__
            }
            utils.print_log_message('Info', message, LOG)
            subscriber.available(nodes)

    def unavailable(self, nodes):
        """Turns nodes unavailable.

        :param nodes: nodes collection to be unavailable.
        """
        for subscriber in self.subscribers.values():
            message = "Unregistering nodes %(nodes)s in subscriber %(subscriber)s" % {
                "nodes": nodes, "subscriber": subscriber.__class__.__name__
            }
            utils.print_log_message('Info', message, LOG)
            subscriber.unavailable(nodes)

    @staticmethod
    def genconfig():
        print("========= Serverlist =========")
        mac_file_path = utils.get_input("Type the path to mac file: ")

        mac_file_path = os.path.realpath(os.path.expanduser(mac_file_path))
        return {"mac_file_path": mac_file_path}


@six.add_metaclass(abc.ABCMeta)
class DiscoveryNodeSubscriber(object):
    """
    This class should be implemented by subscribers.
    """
    @abstractmethod
    def available(self, nodes):
        """Abstract method that turns nodes available.

        :raises NotImplementedException if called directly.
        """
        raise NotImplementedError("NotImplementedException")

    @abstractmethod
    def unavailable(self, nodes):
        """Abstract method that turns nodes unavailable.

        :raises NotImplementedException if called directly.
        """
        raise NotImplementedError("NotImplementedException")
