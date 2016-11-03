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
This module represents the Puller component from oneview_monasca agent.
"""

from oneview_monasca.eventbus.base import DiscoveryNodeSubscriber
from oneview_monasca.publisher.base import PublisherProvider
from oneview_monasca.shared import log as logging
from oneview_monasca.model.status import Status
from oneview_monasca.shared import utils
from threading import Thread
from threading import Lock

import time

LOG = logging.get_logger(__name__)


class Puller(PublisherProvider, DiscoveryNodeSubscriber, Thread):
    """ The Puller is a publisher for Metric Keeper and a Subscriber from a Node
    Discovery. It process status of OneView resources and publish to
    subscribers.

    Thread control:
        stopped: Manage the thread state (running or stopped).
        lock: Manage the access of another publishers to shared data structs to avoid race condition.
    """

    def __init__(self, manager_oneview, refresh_interval, crash_callback, debug=False):
        super(Puller, self).__init__()
        Thread.__init__(self)

        self.debug = debug
        self._manager_oneview = manager_oneview
        self._crash_callback = crash_callback
        self._refresh_interval = int(refresh_interval)

        #  This boolean indicates if it's the first time that the Puller
        #  receives available nodes.
        self._first_available_iteration = True
        self._monitored_nodes = set()

        # Thread attributes control
        self._lock = Lock()
        self._stopped = True

    def stop(self):
        """ Stop the Thread.
        """
        self._stopped = True
        self._Thread__stop()

    def publish(self):
        """ Initialize the process of Component.
        """
        utils.print_log_message('Info', 'Initialize Puller', LOG)

        self._stopped = False
        self.start()

    def available(self, nodes):
        """ Receive a set of nodes to be monitored.

        :param nodes: A set of Node objects.
        """
        updated_servers_hardware = set()
        for node in nodes:
            updated_servers_hardware.add(node.server_hardware_uuid)
            utils.log_actions(node, "discovered", self.debug, LOG)

        self._lock.acquire()
        self._monitored_nodes.update(updated_servers_hardware)
        self._lock.release()

        if self._first_available_iteration:
            self._first_available_iteration = False
            self._process_status()

    def unavailable(self, nodes):
        """ Receive a set of nodes and very if these nodes should be removed
        from monitored nodes.

        To verify, the puller looks at metrics in nodes: if metrics is empty,
        it will remove the node, else it will keep the node in monitored nodes.

        :param nodes: A set of Node objects.
        """
        updated_servers_hardware = set()
        for node in nodes:
            if not node.metrics:
                updated_servers_hardware.add(node.server_hardware_uuid)
                utils.log_actions(node, "removed", self.debug, LOG)

        self._lock.acquire()
        self._monitored_nodes.difference_update(updated_servers_hardware)
        self._lock.release()

    def _process_status(self):
        """ Process status of each OneView resource in the set of monitored
        nodes, creating a Status object and, at last publish a set of statuses
        for subscribers.
        """
        utils.print_log_message('Info', 'Start process status from OneView resources', LOG)

        try:
            states = set()
            # Locking shared resource
            self._lock.acquire()
            for server_hardware_uuid in self._monitored_nodes:
                status, str_timestamp = self._manager_oneview.get_server_hardware_status(server_hardware_uuid)

                if status is not None and str_timestamp:
                    modified_timestamp = utils.parse_timestamp(str_timestamp)
                    states.add(Status(server_hardware_uuid, status, modified_timestamp))

            # Unlocking shared resource
            self._lock.release()

            if states:
                self.status_update(states)
                utils.print_log_message('Info', 'End process status from OneView resources', LOG)

        except Exception as ex:
            self._lock.release()
            self._crash_callback(ex)

    def run(self):
        """ Pull and process status from OneView resources and publish to
        subscribers.
        """
        while True:
            if not self._stopped:
                self._process_status()

            time.sleep(self._refresh_interval)
