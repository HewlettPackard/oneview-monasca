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
Provides interest nodes based on Ironic services.
"""

from ovm_ironic.manager.manager_ironic import ManagerIronic
from ovm_ironic.driver.base import DiscoveryNodeProvider
from ovm_ironic.shared import log as logging
from ovm_ironic.shared import utils as utils
from threading import Thread
from threading import Lock

import time

LOG = logging.get_logger(__name__)


class DiscoveryNodeIronicProvider(DiscoveryNodeProvider, Thread):
    """
    This class provides interest nodes associated with Ironic service.

    Thread control:
        stopped: Manage the thread state (running or stopped).
        lock: Manage the access of another publishers to shared data structs to
        avoid race condition.
    """
    def __init__(self, conf, manager_ironic=None, debug=False):
        super(DiscoveryNodeIronicProvider, self).__init__(debug)
        Thread.__init__(self)

        self._conf = conf
        self._manager_ironic = manager_ironic

        # Thread control
        self._lock = Lock()
        self._stopped = True

    def _initialize(self):
        """
        Build data structure that will used.
        """
        utils.print_log_message('Info', 'Initialize Discovery Node Ironic Provider', LOG)

        self._interest_nodes = set()
        self._retry_interval = int(self._conf.DEFAULT.retry_interval)
        if not self._manager_ironic:
            self._manager_ironic = ManagerIronic(
                username=self._conf.ironic.admin_user,
                password=self._conf.ironic.admin_password,
                auth_url=self._conf.ironic.auth_url,
                tenant_name=self._conf.ironic.admin_tenant_name,
                api_version=self._conf.ironic.ironic_api_version,
                insecure=self._conf.ironic.insecure,
                max_attempt=self._conf.DEFAULT.auth_retry_limit,
                debug=self.debug
            )

    def stop(self):
        """
        Stop the thread.
        """
        self._stopped = True
        self._Thread__stop()

    def discover(self):
        """
        Start discovery.
        """
        try:
            self._initialize()

            # Starting Thread
            self._stopped = False
            self.start()
        except Exception as ex:
            message = 'Cannot starting ironic plugin, fatal error caused by: %s.' % ex
            utils.print_log_message('Info', message, LOG)

    def _pull_nodes(self):
        """
        Verify if exists changes in interest nodes and notify subscribers.
        """
        try:
            utils.print_log_message(
                'Debug', 'Pulling Ironic nodes...', LOG, self.debug)

            nodes = self._manager_ironic.get_node_list()
            interest_nodes = self._manager_ironic.get_nodes_associated_oneview(nodes)

            message = "%s Ironic interest nodes has been taken." % len(interest_nodes)
            utils.print_log_message('Info', message, LOG)

            if interest_nodes != self._interest_nodes:
                # Check if there new nodes to add in list of interest nodes
                added_nodes = interest_nodes - self._interest_nodes
                if added_nodes:
                    self._interest_nodes.update(added_nodes)
                    self._lock.acquire()
                    self.available(added_nodes)
                    self._lock.release()

                # Check if there node to be removed from list of interest nodes
                removed_nodes = self._interest_nodes - interest_nodes
                if removed_nodes:
                    self._interest_nodes.difference_update(removed_nodes)
                    self._lock.acquire()
                    self.unavailable(removed_nodes)
                    self._lock.release()

        except Exception as ex:
            self.stop()
            utils.print_log_message('Error', ex, LOG)

    def run(self):
        """Runs the thread.
        """
        while True:
            if not self._stopped:
                self._pull_nodes()

            time.sleep(self._retry_interval)
