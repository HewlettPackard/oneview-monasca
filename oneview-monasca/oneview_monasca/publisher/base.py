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
"""Provides for publish components.
"""
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class PublisherProvider(object):
    """
    This class represent a provider for publisher components.
    """
    def __init__(self):
        super(PublisherProvider, self).__init__()
        self.subscribers = {}

    def subscribe(self, subscriber):
        """Subscribe a listener.
        :param subscriber: the listener component.
        """
        key = subscriber.__class__.__name__
        if key not in self.subscribers.keys():
            self.subscribers[key] = subscriber

    def unsubscribe(self, subscriber):
        """Unsubscribe a listener
        :param subscriber: the listener component.
        """
        key = subscriber.__class__.__name__
        if key in self.subscribers.keys():
            del self.subscribers[key]

    def status_update(self, states):
        """
        Send a set of Status from OneView resources.
        :param states: Set of :class: `Status` with new about OneView resources.
        """
        for subscriber in self.subscribers.values():
            subscriber.status_update(states)


@six.add_metaclass(abc.ABCMeta)
class PublisherSubscriber(object):
    """
    This class represent a subscriber for publisher components.
    """
    def __init__(self):
        super(PublisherSubscriber, self).__init__()

    @abc.abstractmethod
    def status_update(self, states):
        """
        Receive a set of Status from OneView resources.
        :param states: Set of :class: `Status` with new about OneView resources.
        """
        raise Exception("NotImplementedException")
