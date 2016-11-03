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

""" This module represents the Fault Tolerance Controller component from oneview_monasca agent."""

from oneview_monasca.shared import constants as const
from oneview_monasca.shared import log as logging
from oneview_monasca.shared import utils
from tooz import coordination

import time
import uuid

LOG = logging.get_logger(__name__)


class Coordinator(object):
    """
    Coordinator is the controller for multiple virtual machines that are running Monasca OneViewD.
    It is responsible to choosing an agent who was sleeping if the current metric publisher agent fall down.
    In this context, the publisher is called leader, because is the only who is really pushing metrics between all the
    coordinators running at this current time. The control of who is running is made by tooz, an OpenStack lib
    """

    def __init__(self, conf, taskto_run):
        """ This class implements a coordinator to run a specific method when it becomes a leader.

        :param conf: File containing the information necessary to start a new coordinator using tooz.
        :param taskto_run: Method that must be called when this Coordinator become the group leader.
        """
        utils.print_log_message('Info', 'Initialize Coordinator', LOG)
        self._conf = conf
        self._taskto_run = taskto_run
        self._coordinator_url = self._conf.coordinator_url
        self._id = self._generate_id()
        self._coordinator = coordination.get_coordinator(self._coordinator_url, self._id)
        self._group = self._conf.group_name
        self._stopped = False
        self._im_a_leader = False

    def start(self):
        """ Start the _coordinator, introduce it into a group, run the watchers in a new thread and callback the
        taskto_run when it is elected leader.
        """
        utils.print_log_message('Info', 'Initializing a new coordinator...', LOG)
        self._coordinator.start()
        self._coordinator.get_groups().get()
        self._coordinator.watch_join_group(self._group, self._join_group_callback)
        self._coordinator.watch_leave_group(self._group, self._leave_group_callback)
        self._coordinator.watch_elected_as_leader(self._group, self._leader_elected_callback)
        self._join_group()
        self._run_watchers()

    def stop(self):
        """ Stop the _coordinator if necessary and set the _stopped flag. """
        if not self._stopped:
            self._stopped = True
            self._coordinator.stop()

    @staticmethod
    def _generate_id():
        """ Generate and id for the _coordinator. """
        return '%s-%s' % (const.PREFIX_ID_COORD, uuid.uuid4())

    def _im_leader(self):
        """ Check if this coordinator is the current leader. """
        return self._im_a_leader

    def _join_group(self):
        """ Introduce the _coordinator for a group specified in the conf. If the group do not exists yet, this method
        create a new with the name specified.
        """
        if self._group not in self._coordinator.get_groups().get():
            self._coordinator.create_group(self._group).get()
        self._coordinator.join_group(self._group).get()

    def _join_group_callback(self, event):
        """ Callback to log when the _coordinator ingress the group. """
        message = 'The member {0} joined group {1}'.format(self._id, self._group)
        utils.print_log_message('Info', message, LOG)

    def _leader_elected_callback(self, event):
        """ Callback to log when a member is the new group leader and start a new thread calling back the taskto_run.
        :param event: A LeaderElected event
        """
        self._im_a_leader = True
        message = 'The member {0} is now running the Daemon'.format(event.member_id)
        utils.print_log_message('Info', message, LOG)
        self._taskto_run()

    @staticmethod
    def _leave_group_callback(event):
        """ Callback to log when a member leave the group.
        :param event: An instance of tooz.coordination.MemberJoinedGroup
        """
        message = 'The member {0} left group {1}'.format(event.member_id, event.group_id)
        utils.print_log_message('Info', message, LOG)

    def _run_watchers(self):
        """ Run tooz watchers for activities in groups. """
        while not self._stopped:
            self._coordinator.run_watchers()
            time.sleep(const.HEARTBEAT_INTERVAL)

    def step_down(self):
        """ Stand down as the group leader if we are.
        """
        self._coordinator.stand_down_group_leader(self._group)
