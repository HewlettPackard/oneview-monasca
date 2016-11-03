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
This module represents the Keeper component from oneview_monasca agent.
"""

from oneview_monasca.eventbus.base import DiscoveryNodeSubscriber
from oneview_monasca.model.measurement import Measurement
from oneview_monasca.publisher.base import PublisherSubscriber
from oneview_monasca.shared import log as logging
from oneview_monasca.shared import utils
from threading import Thread
from threading import Lock

import time

LOG = logging.get_logger(__name__)


class Keeper(PublisherSubscriber, DiscoveryNodeSubscriber, Thread):
    """
    This class represents the Keeper component from oneview_monasca
    agent.

    The Keeper it's responsible for store and public all newer health
    status measurements from OneView resources received from any of its
    publishers, all metrics are published into Monasca.

    Thread control:
        stopped: Manage the thread state (running or stopped).
        lock: Manage the access of another publishers to shared data structs to avoid race condition.
    """

    def __init__(self, oneview_manager, monasca_manager, batch_time, debug=False):
        super(Keeper, self).__init__()
        Thread.__init__(self)

        self.debug = debug
        self._metric_storage = {}
        self._batch_time = int(batch_time)

        self._manager_oneview = oneview_manager
        self._manager_monasca = monasca_manager

        # Thread attributes control
        self._lock = Lock()
        self._stopped = True

    def stop(self):
        """ Stops the Thread """
        self._stopped = True
        self._Thread__stop()

    def publish(self):
        """ Start the  Keeper """
        utils.print_log_message('Info', 'Initialize Keeper', LOG)

        self._stopped = False
        self.start()

    def status_update(self, states):
        """
        This method update the data structure with all newer status
        information from nodes, and pushes all this new information to
        Monasca.
        """
        valid_metrics = []
        for status in states:
            uuid = status.server_hardware_uuid
            updated = self._update_status(status)
            if updated:
                self._update_meta(uuid)
                self._lock.acquire()
                node_metrics = self._create_measurements(uuid)
                self._lock.release()
                valid_metrics.extend(node_metrics)

        if len(valid_metrics) > 0:
            self._manager_monasca.send_metrics(valid_metrics)
        else:
            utils.print_log_message('Info', 'There is no metrics to be sent', LOG)

    def _update_status(self, status):
        """
        This method update the Keeper data structure for a given status if
        valid.

        :param status: A Status object representing a server hardware state from OneView.
        :rtype: A :boolean: - True, if the server hardware have a newer status.
        """
        result = False
        uuid = status.server_hardware_uuid

        # Locking shared resource
        self._lock.acquire()
        if uuid in self._metric_storage:
            stored_status = self._metric_storage[uuid].get('status')

            if stored_status is None:
                self._metric_storage[uuid]['status'] = status
                utils.print_log_message('Info', "gathered first status for %s:%s" % (uuid, status), LOG)
                result = True

            elif status.modified_timestamp >= stored_status.modified_timestamp:
                self._metric_storage[uuid]['status'] = status
                result = True

        # Unlocking shared resource
        self._lock.release()
        return result

    def _update_meta(self, uuid):
        """
        This method update the meta value information for a given uuid.

        :param uuid: The server hardware uuid from monitored OneView resource
        """
        # Locking shared resource
        self._lock.acquire()

        status = self._metric_storage[uuid]['status'].status
        self._metric_storage[uuid]['meta'] = \
            self._manager_oneview.get_server_hardware_alerts(uuid, status)

        # Unlocking shared resource
        self._lock.release()

    def _create_measurements(self, uuid):
        """
        This method create a list of measurements for a given uuid.

        :param uuid: The server hardware uuid from monitored OneView resource
        :rtype: A list with all Measurements objects for the given uuid.
        """
        measurements_list = []
        for metric in self._metric_storage[uuid]['metrics']:
            stored_status = self._metric_storage[uuid].get('status')
            if stored_status is not None:
                meta = self._metric_storage[uuid]['meta']
                value = stored_status.status

                measurement = Measurement(metric.name, value, metric.dimensions, meta)
                measurements_list.append(measurement)

        return measurements_list

    def available(self, nodes):
        """
        This method updates the data structure adding new nodes or new
        information about nodes that are already stored.
        """
        # Locking shared resource
        self._lock.acquire()

        for node in nodes:
            if node.server_hardware_uuid not in self._metric_storage:
                utils.log_actions(node, "discovered", self.debug, LOG)
                self._metric_storage[node.server_hardware_uuid] = {
                    'metrics': node.metrics, 'status': None, 'meta': {}
                }
            else:
                self._metric_storage[node.server_hardware_uuid]['metrics'] = node.metrics

        # Unlocking shared resource
        self._lock.release()

    def unavailable(self, nodes):
        """
        This method updates the data structure removing nodes or information
        about nodes that are already stored.
        """
        # Locking shared resource
        self._lock.acquire()

        for node in nodes:
            del self._metric_storage[node.server_hardware_uuid]

        # Unlocking shared resource
        self._lock.release()

    def run(self):
        """
        This method pull all stored information in data structure and send to
        Monasca
        """
        while True:
            time.sleep(self._batch_time)

            if not self._stopped:
                try:
                    all_measurements = []
                    # Locking shared resource
                    self._lock.acquire()
                    for uuid in self._metric_storage:
                        measurements = self._create_measurements(uuid)
                        all_measurements.extend(measurements)

                    # Unlocking shared resource
                    self._lock.release()
                    self._manager_monasca.send_metrics(all_measurements)
                    utils.print_log_message(
                        'Debug', 'Finished send actual metrics from data structure', LOG, self.debug)
                except Exception as ex:
                    utils.print_log_message('Error', "Keeper failed: %s" % ex.message, LOG)
