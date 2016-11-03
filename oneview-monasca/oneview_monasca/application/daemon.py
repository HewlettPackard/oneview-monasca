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

"""Creates and start a coordinator to start the application.
"""

from oneview_monasca.manager.manager_oneview import ManagerOneView
from oneview_monasca.manager.manager_monasca import ManagerMonasca
from oneview_monasca.eventbus.node_discovery import EventBUS
from oneview_monasca.eventbus.priority import PriorityENUM
from oneview_monasca.publisher.keeper import Keeper
from oneview_monasca.publisher.puller import Puller
from oneview_monasca.shared import log as logging
from oneview_monasca.publisher.scmb import SCMB
from oneview_monasca.shared import utils
from coordinator import Coordinator

import time

LOG = logging.get_logger(__name__)


class Daemon(object):
    """
    The Daemon is responsible to create and start a coordinator to start the application.
    The application will be started only when this coordinator is elected leader of the
    specific group in tooz/zookeeper for the Monasca/OneView. When it happens, a new
    SCMB object is called and it start to run the pushing actions to Monasca from
    OneView appliance, both specified in the configuration file.
    """
    def __init__(self, conf):
        utils.print_log_message('Info', 'Initialize Daemon', LOG)

        self._conf = conf
        self._coordinator = None
        self._eventbus = None
        self._keeper = None
        self._puller = None
        self._scmb = None

        # Setting debug mode
        self.debug = True if conf.DEFAULT.debug == 'true' else False

    def _start(self):
        """Initialized the publishers.
        """
        utils.print_log_message('Info', 'Creating EventBus', LOG)
        self.eventbus.start()

        utils.print_log_message('Info', 'Creating Publishers', LOG)
        # Create publishers.
        self.keeper.publish()
        self.puller.publish()
        self.scmb.publish()

        utils.print_log_message('Info', 'Subscribe Monasca publisher to intern publishers', LOG)
        # Subscribe intern publishers in Monasca publisher.
        self.scmb.subscribe(self.keeper)
        self.puller.subscribe(self.keeper)

        utils.print_log_message('Info', 'Subscribe publishers to eventbus', LOG)
        # Subscribe publisher to receive notification of eventbus.
        self.eventbus.subscribe(self.keeper, PriorityENUM.HIGH)
        self.eventbus.subscribe(self.scmb)
        self.eventbus.subscribe(self.puller)

    def _stop(self):
        """Restart the publishers.
        """
        time.sleep(5)
        utils.print_log_message('Info', 'Unsubscribe publishers to eventbus', LOG)
        # Unsubscribe publisher to receive notification of eventbus.
        self.eventbus.unsubscribe(self.puller)
        self.eventbus.unsubscribe(self.scmb)
        self.eventbus.unsubscribe(self.keeper)

        utils.print_log_message('Info', 'Unsubscribe Monasca publisher to intern publishers', LOG)
        # Unsubscribe intern publishers in Monasca publisher.
        self.puller.unsubscribe(self.keeper)
        self.scmb.unsubscribe(self.keeper)

        utils.print_log_message('Info', 'Stopping publishers and discarding its reference in Daemon', LOG)
        # Stopping publishers.
        self.keeper.stop()
        self.puller.stop()
        self.scmb.stop()
        # Discarding publishers reference in Daemon
        self.scmb = self.puller = self.keeper = None

        utils.print_log_message('Info', 'Oneview Monasca Daemon stopped, preparing to re-initialize', LOG)

    def _get_manager_oneview(self):
        """Get a instance of Manager Oneview
        """
        return ManagerOneView(
            host=self._conf.oneview.host,
            username=self._conf.oneview.username,
            password=self._conf.oneview.password,
            max_attempt=self._conf.DEFAULT.auth_retry_limit,
            certificates_directory=self._conf.DEFAULT.scmb_certificate_dir
        )

    def _get_manager_monasca(self):
        """Get a instance of Manager Monasca
        """
        return ManagerMonasca(
            auth_url=self._conf.openstack.auth_url,
            username=self._conf.openstack.auth_user,
            password=self._conf.openstack.auth_password,
            project_name=self._conf.openstack.auth_tenant_name,
            api_version=self._conf.openstack.monasca_api_version,
            debug=self.debug
        )

    @property
    def eventbus(self):
        """Get a instance of eventbus
        """
        if self._eventbus is None:
            self._eventbus = EventBUS(self._conf, debug=self.debug)

        return self._eventbus

    @property
    def keeper(self):
        """Get a instance of keeper
        """
        if self._keeper is None:
            self._keeper = Keeper(
                self._get_manager_oneview(),
                self._get_manager_monasca(),
                self._conf.DEFAULT.batch_publishing_interval,
                debug=self.debug
            )

        return self._keeper

    @keeper.setter
    def keeper(self, value):
        """Set keeper property with input value

        :param value: the new value of keeper property
        """
        self._keeper = value

    @property
    def puller(self):
        """Get a instance of puller
        """
        if self._puller is None:
            self._puller = Puller(
                self._get_manager_oneview(),
                self._conf.DEFAULT.periodic_refresh_interval,
                self.crash_callback,
                debug=self.debug
            )

        return self._puller

    @puller.setter
    def puller(self, value):
        """Set puller property with input value

        :param value: the new value of puller property
        """
        self._puller = value

    @property
    def scmb(self):
        """Get a instance of scmb
        """
        if self._scmb is None:
            self._scmb = SCMB(
                self._get_manager_oneview(),
                self._conf.oneview.host,
                self._conf.DEFAULT.auth_retry_limit,
                self.crash_callback,
                debug=self.debug
            )

        return self._scmb

    @scmb.setter
    def scmb(self, value):
        """Set scmb property with input value

        :param value: the new value of scmb property
        """
        self._scmb = value

    @property
    def coordinator(self):
        """Get a instance of coordinator to running fault tolerance
        """
        if self._coordinator is None:
            self._coordinator = Coordinator(self._conf.tooz, self._start)

        return self._coordinator

    @coordinator.setter
    def coordinator(self, value):
        """Set coordinator property with input value

        :param value: the new value of coordinator property
        """
        self._coordinator = value

    def start(self):
        """Starts the coordinator.
        """
        try:
            self.coordinator.start()
        except Exception as e:
            message = e.message + ": The agent is running without active/passive fault tolerance."
            utils.print_log_message('Warn', message, LOG)

            self.coordinator = None
            self._start()

    def crash_callback(self, exc_obj):
        """The function to restarting the agent server after fatal error in some publisher

        :param exc_obj: The exception object raised from a publisher
        """
        utils.print_log_message('Error', exc_obj, LOG)
        self._stop()

        if self._coordinator is not None:
            self.coordinator.step_down()
        else:
            self._start()
