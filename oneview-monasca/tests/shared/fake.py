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

""" This module contains the most important fake classes to be used
into the tests.
"""

from oneview_monasca.eventbus.base import DiscoveryNodeSubscriber
from oneview_monasca.publisher.base import PublisherSubscriber
from oneview_monasca.publisher.base import PublisherProvider
from oneview_monasca.shared import log as logging

from pika.adapters.blocking_connection import SelectConnection
from datetime import datetime

LOG = logging.get_logger(__name__)


class FakeDiscoveryNodeProvider(object):
    """ This class is a fake DiscoveryNodeProvider to be used into the tests.
    It's contains the method needed to test.
    """
    def __init__(self):
        """ Fake DiscoveryNodeProvider constructor.
        Init a dict of subscribers.
        """
        self.subscribers = {}

    def subscribe(self, subscriber):
        """ Subscribe a component to receive nodes discoveded. Add subscriber
        to subscribers dict.

        :param subscriber: Component to subscribe.
        """
        key = subscriber.__class__.__name__
        if key not in self.subscribers.keys():
            self.subscribers[key] = subscriber

    def unsubscribe(self, subscriber):
        """ Remove a subscriber from subscribers dict.

        :param subscriber: Subscriber to be removed from subscribers dict.
        """
        key = subscriber.__class__.__name__
        if key in self.subscribers.keys():
            del self.subscribers[key]

    def available(self, nodes):
        """ Made a set of nodes received as parameter available for each
        subscriber in subscribers dict.

        :param nodes: Set of nodes to be made available.
        """
        for subscriber in self.subscribers.values():
            subscriber.available(nodes)

    def unavailable(self, nodes):
        """ Made a set of nodes received as parameter unavailable for each
        subscriber in subscribers dict.
        """
        for subscriber in self.subscribers.values():
            subscriber.unavailable(nodes)


class FakeHLMPluginProvider(FakeDiscoveryNodeProvider):
    """ This class represents a fake HLMPluginProvider inheriting from
    DiscoveryNodeProvider.
    """
    def __init__(self):
        """ FakeHLMPluginProvider constructor
        """
        super(FakeHLMPluginProvider, self).__init__()


class FakeIronicPluginProvider(FakeDiscoveryNodeProvider):
    """ This class represents a fake IronicPluginProvider inheriting from
    DiscoveryNodeProvider.
    """
    def __init__(self):
        super(FakeIronicPluginProvider, self).__init__()


class FakeModelNode(object):
    """ This class represents a fake Node object used by plugins

    :param server_hardware_uuid: A string, the UUID from the Oneview resource.
    :param metrics: A set, the metrics to the server hardware.
    """
    def __init__(self, server_hardware_uuid, metrics=set()):
        self.server_hardware_uuid = server_hardware_uuid
        self.metrics = metrics


class FakeModelMetric(object):
    """ This class represents a fake Node object used by plugins

    :param name: A string, the name of metric.
    :param dimensions: A dict, the dimensions of metric.
    """
    def __init__(self, name, dimensions={}):
        self.name = name
        self.dimensions = dimensions


class FakeComponent(DiscoveryNodeSubscriber):
    """ This class is a fake DiscoveryNodeSubscriber to be used into the tests.
    It's contains the method needed to test.
    """
    def __init__(self, name):
        """ Fake DiscoveryNodeSubscriber constructor.
        """
        super(FakeComponent, self).__init__()
        self.name = name
        self.last_updated = None
        self.__nodes = {}

    def get_nodes(self):
        """ Return the nodes available in the component.
        """
        return set(self.__nodes.values())

    def available(self, nodes):
        """ Receive a set of nodes to add to __nodes
        """
        self.last_updated = datetime.now()
        for node in nodes:
            self.__nodes[node.server_hardware_uuid] = node
        LOG.info('[%s] available: %s' % (self.name, nodes))

    def unavailable(self, nodes):
        """ Receive a set of nodes to remove from __nodes if the metrics of each
        node is empty.
        """
        self.last_updated = datetime.now()
        for node in nodes:
            if len(node.metrics) == 0:
                del self.__nodes[node.server_hardware_uuid]
            else:
                self.__nodes[node.server_hardware_uuid].metrics = node.metrics
        LOG.info('[%s] unavailable: %s' % (self.name, nodes))


class FakeManagerOneview:
    """ This class represents a fake Manager OneView.
    """
    def __init__(self):
        pass

    @staticmethod
    def get_server_hardware_status(status=None):
        """ Return a server hardware status or/and date timezone
        """
        if status:
            return {'status': 'OK'}
        else:
            return {'status': 'Warning', 'modified': '2014-08-07T11:00:11.467Z'}

    @staticmethod
    def get_server_hardware(uuid):
        """ Return a dict to representing a fake server hardware
        """
        return {'uuid': uuid}

    @staticmethod
    def get_server_hardware_alerts(sh_uuid=None):
        """ Return fakes alerts associated a server hardware
        """
        if not sh_uuid:
            return {}
        else:
            return [{'uri': '/server-hardware/' + sh_uuid}]


class FakeManagerMonasca:
    """ This class represents a fake Manager Monasca.
    """
    def __init__(self, auth_url, username, password, project_name, api_version):
        pass

    @staticmethod
    def send_metrics(measurements):
        """
        Update a list of metric dictionary  measurements to be in the
        Metric format that Monasca allow and sends them in one request.
        :param measurements: A list of Measurement objects to send to Monasca.
        """
        pass


class FakePuller(FakeComponent, PublisherProvider):
    """ This class represents a fake Puller.
    """
    def __init__(self):
        """ Fake Puller constructor.
        """
        super(FakePuller, self).__init__('FakePuller')


class FakeKeeper(FakeComponent, PublisherSubscriber):
    """ This class represents a fake keeper.
    """
    def __init__(self):
        """ Fake Keeper constructor.
        """
        super(FakeKeeper, self).__init__('FakeKeeper')
        self.states = set()

    def status_update(self, states):
        """ Receive a set of states of monitored nodes.
        """
        self.states.update(states)


class FakeArgs:
    """ This class represents a fake args parse.
    """
    def __init__(self):
        self.config_file = '~/oneview_monasca.conf'


class FakeExtension:
    """ This class represents a fake Extension of stevedore module
    """
    def __init__(self, name):
        self.name = name


class FakeSelectConnection(SelectConnection):
    is_closed = None
    is_closing = None
    is_open = None
    outbound_buffer = None
    _channels = None
    ioloop = None


def fake_crash_callback(exc_obj=None):
    """ This function represents the real crash function of
    oneview-monasca.
    """
    pass
