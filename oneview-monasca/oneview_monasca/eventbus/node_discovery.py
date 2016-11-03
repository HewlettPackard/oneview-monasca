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

"""Receives events from multiple plugins, sets the metrics and publishes them to listeners.
"""

from oneview_monasca.eventbus.priority import PriorityENUM
from oneview_monasca.shared import constants as const
from oneview_monasca.shared import log as logging
from oneview_monasca.shared import utils

import time
import copy

LOG = logging.get_logger(__name__)


class EventBUS(object):
    """
    This class is responsible for receiving events from multiple plugins,
    set the metrics by a single identifier (server_hardware_uuid) and publish to
    listeners.
    """
    _metaclass__ = utils.SingletonType

    def __init__(self, conf, debug=False):
        super(EventBUS, self).__init__()

        self._conf = conf
        self.debug = debug

        self._initialize()

    def _initialize(self):
        """
        Build data structure that will used.
        """
        self._drivers = {}
        self._subscribers = {
            PriorityENUM.LOW: set(),
            PriorityENUM.HIGH: set()
        }
        self._events = {}

    def _initialize_drivers(self):
        """
        Find extensions by namespace, initialize driver and start
        discover method in drivers found.
        """
        utils.print_log_message('Debug', 'Initialize Event BUS', LOG, self.debug)

        names = utils.list_names_driver(const.NAMESPACE_DISCOVERY_NODES)
        for name in names:
            utils.print_log_message('Info', 'Find driver [%s]' % name, LOG)
            try:
                if name not in self._drivers:
                    self._drivers[name] = utils.load_class_by_alias(
                        const.NAMESPACE_DISCOVERY_NODES,
                        name
                    )(self._conf, debug=self.debug)
                    self._drivers[name].subscribe(self)
                    self._drivers[name].discover()
            except ImportError:
                # Try load names found.
                utils.print_log_message('Info', 'Driver [%s] not found' % name, LOG)
            except Exception as ex:
                utils.print_log_message('Error', ex, LOG)
                raise

    def start(self):
        """
        Start drivers.
        """
        self._initialize_drivers()

    def stop(self):
        """
        Stop drivers.
        """
        try:
            for driver in self._drivers.values():
                driver.stop()

            # Clean the data structure.
            self._initialize()

        except Exception as e:
            utils.print_log_message('Error', e, LOG)

    def length_subscribers(self, priority=None):
        """
        Get length of the subscribers.

        :param priority: A PriorityENUM, the priority's value.
        :rtype: A :int: length by priority if not None otherwise all.
        """
        utils.print_log_message('Debug', 'length_subscribers, Priority[%s]' % priority, LOG)
        if priority is not None:
            return len(self._subscribers[priority])

        return len(self._subscribers[PriorityENUM.HIGH]) + len(self._subscribers[PriorityENUM.LOW])

    def _copy_event(self, node):
        """
        Ensure that it is Immutable.
        """
        if node.server_hardware_uuid in self._events:
            new_node = copy.deepcopy(self._events[node.server_hardware_uuid])
            # update set _events, adding metrics from node
            new_node.metrics.update(node.metrics)
        else:
            new_node = copy.deepcopy(node)

        self._events[node.server_hardware_uuid] = new_node

    def _resolve_available_metrics(self, nodes):
        """
        Group metrics by server hardware UUID.
        """
        updated_nodes = set()
        for node in nodes:
            self._copy_event(node)
            updated_nodes.add(self._events[node.server_hardware_uuid])

        return updated_nodes

    def _resolve_unavailable_metrics(self, nodes):
        """
        Verify and remove metrics of nodes that not should be monitored.
        """
        updated_nodes = set()
        for node in nodes:
            # Update set events, removing elements found in nodes
            self._events[node.server_hardware_uuid].metrics.difference_update(node.metrics)
            updated_nodes.add(self._events[node.server_hardware_uuid])

        return updated_nodes

    def available(self, nodes):
        """
        Notify subscribers with events of available nodes.
        """
        updated_nodes = self._resolve_available_metrics(nodes)
        if updated_nodes:
            # First notify subscribers of highest priority
            for subscribe in self._subscribers[PriorityENUM.HIGH]:
                subscribe.available(updated_nodes)

            time.sleep(1)

            # Second notify subscribers of lower priority
            for subscribe in self._subscribers[PriorityENUM.LOW]:
                subscribe.available(updated_nodes)

    def unavailable(self, nodes):
        """
        Notify subscribers with events of unavailable nodes.
        """
        updated_nodes = self._resolve_unavailable_metrics(nodes)
        # First notify subscribers of lower priority to not publish
        # in listener components of highest priority.
        for subscribe in self._subscribers[PriorityENUM.LOW]:
            subscribe.unavailable(updated_nodes)

        time.sleep(1)

        # Second notify subscribers of highest priority that will
        # not receive publication from listener components of lower priority.
        for subscribe in self._subscribers[PriorityENUM.HIGH]:
            subscribe.unavailable(updated_nodes)

    def subscribe(self, subscriber, priority=PriorityENUM.LOW):
        """
        Subscribe a subscriber by priority. Set priority low if is
        a listener component that publish information, otherwise if
        listener component is a information consumer, then set to high.
        """
        utils.print_log_message('Info', 'Subscribe %s with priority %s' % (subscriber, priority), LOG)
        self._subscribers[priority].add(subscriber)
        if len(self._events.values()) > 0:
            subscriber.available(set(self._events.values()))

    def unsubscribe(self, subscriber):
        """
        Unsubscribe a subscriber if subscribed.
        """
        for priority in self._subscribers.keys():
            if subscriber in self._subscribers[priority]:
                # removes subscriber from set subscribers[priority] if present
                self._subscribers[priority].discard(subscriber)
