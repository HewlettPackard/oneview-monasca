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
"""Provides interest nodes based on compute services.
"""

from ovm_serverlist.manager.manager_server_list import ManagerServerList
from ovm_serverlist.manager.manager_oneview import ManagerOneView
from ovm_serverlist.driver.base import DiscoveryNodeProvider
from ovm_serverlist.shared import utils as utils
from ovm_ironic.shared import log as logging

from threading import Thread
from threading import Lock
from time import sleep

LOG = logging.get_logger(__name__)


class DiscoveryNodeServerListProvider(DiscoveryNodeProvider, Thread):
    """
    This class provides interest nodes associated with compute service.

    Thread control:
        stopped: Manage the thread state (running or stopped).
        lock: Manage the access of another publishers to shared data structs to
        avoid race condition.
    """
    def __init__(self, conf, manager_oneview=None, debug=False):
        super(DiscoveryNodeServerListProvider, self).__init__(debug)
        Thread.__init__(self)

        self._conf = conf
        self._manager_oneview = manager_oneview
        # Thread control
        self._lock = Lock()
        self._stopped = True

    def _initialize(self):
        """Build data structure that will used.
        """
        message = 'Initializing Discovery Node ServerList Provider...'
        utils.print_log_message('Info', message, LOG)

        self._interest_nodes = set()
        self._retry_interval = int(self._conf.DEFAULT.retry_interval)
        if not self._manager_oneview:
            self._manager_oneview = ManagerOneView(
                host=self._conf.oneview.host,
                username=self._conf.oneview.username,
                password=self._conf.oneview.password,
                max_attempt=self._conf.DEFAULT.auth_retry_limit,
            )

        self._manager_server_list = ManagerServerList(
            mac_file_path=self._conf.serverlist.mac_file_path,
            manager_oneview=self._manager_oneview,
            debug=self.debug
        )
        # Loading from mac file
        self._manager_server_list.load_mac_file()

    def stop(self):
        """Stops the thread.
        """
        self._stopped = True
        self._Thread__stop()

    def discover(self):
        """
        Starts discovery.
        """
        try:
            self._initialize()

            # Starting Thread
            self._stopped = False
            self.start()
        except Exception as ex:
            message = 'Cannot starting server list plugin, fatal error caused by: %s.' % ex
            utils.print_log_message('Error', message, LOG)

    def _pull_nodes(self):
        """Verifies if exists changes in interest nodes and notify subscribers.
        """
        try:
            utils.print_log_message('Debug', 'Pulling ServerList nodes...', LOG, self.debug)

            interest_nodes = self._manager_server_list.get_nodes_associated_oneview()

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

            sleep(self._retry_interval)
