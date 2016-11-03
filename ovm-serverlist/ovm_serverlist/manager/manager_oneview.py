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
Manages the OneView Component
"""

from ovm_serverlist.shared.exceptions import LoginFailException
from ovm_serverlist.shared.exceptions import HTTPFailException
from abstract_manager_oneview import AbstractManagerOneView
from ovm_serverlist.shared import constants as const
from ovm_serverlist.shared import log as logging
from ovm_serverlist.shared import utils as utils

from hpOneView.oneview_client import OneViewClient
from hpOneView.exceptions import HPOneViewException

LOG = logging.get_logger(__name__)


class ManagerOneView(AbstractManagerOneView):
    """
    The OneView Manager.
    """
    def __init__(self, host, username, password, max_attempt=1):
        super(ManagerOneView, self).__init__()

        self.__host = host
        self.__username = username
        self.__password = password
        self.__max_attempt = int(max_attempt)

    def _get_server_hardware_uuid(self, mac):
        """Gets the  server hardware based on the mac of any associated resource.

        :param mac: A string, the MAC's name.
        :rtype: a String with the server hardware uuid associated to the mac
                None if the mac does not have a server hardware uuid.
        """
        try:
            client = OneViewClient({
                'ip': self.__host,
                'credentials': {'userName': self.__username, 'password': self.__password}
            })
            servers = client.server_hardware.get_all()
            for server in servers:
                if server and server['portMap'] and server['portMap']['deviceSlots']:
                    for slot in server['portMap']['deviceSlots']:
                        if slot['physicalPorts']:
                            for port in slot['physicalPorts']:
                                if mac == port['mac']:
                                    return server['uuid']
                                elif port['virtualPorts']:
                                    for vport in port['virtualPorts']:
                                        if mac == vport['mac']:
                                            return server['uuid']

            return None

        except HPOneViewException as hpex:
            if const.HTTP_ERROR_400 in str(hpex):
                utils.print_log_message('Error', const.HTTP_ERROR_400, LOG)
                raise HTTPFailException(const.HTTP_ERROR_400)

            elif const.LOGIN_FAILED in str(hpex):
                utils.print_log_message('Error', const.LOGIN_FAILED, LOG)
                raise LoginFailException(const.LOGIN_FAILED)

            else:
                message = 'Unexpected error: %(message)s' % {'message': str(hpex)}
                utils.print_log_message('Error', message, LOG)
                raise hpex
        except Exception as ex:
            utils.print_log_message('Error', 'Critical Error >>>>>>> %s' % str(ex), LOG)
            raise

    def get_server_hardware_uuid(self, mac):
        """Call the function get_server_hardware_uuid encapsulate into try_execute function
        """
        return utils.try_execute(self._get_server_hardware_uuid, self.__max_attempt, 2000, mac)
