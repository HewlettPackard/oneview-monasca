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
This module provide an Manager OneView that is the concrete class of Abstract
OneView Manager that is used to create a channel between the OneView Rest API
and the publishers.
"""

from oneview_monasca.shared.exceptions import LoginFailException
from oneview_monasca.shared.exceptions import HTTPFailException
from abstract_manager_oneview import AbstractManagerOneView
from oneview_monasca.shared import constants as const
from hpOneView import connection, security, activity
from hpOneView.exceptions import HPOneViewException
from hpOneView.oneview_client import OneViewClient
from oneview_monasca.shared import log as logging
from oneview_monasca.shared import utils

import ssl

LOG = logging.get_logger(__name__)


class ManagerOneView(AbstractManagerOneView):
    """
    The concrete Manager OneView class
    """
    def __init__(self, host, username, password, max_attempt=0, certificates_directory=None):
        super(ManagerOneView, self).__init__()

        self._host = host
        self._username = username
        self._password = password
        self._max_attempt = int(max_attempt)
        self._directory = certificates_directory

    def get_server_hardware_status(self, uuid, status=None):
        """ Get server hardware status and returns

        :param uuid: The uuid of an specific server hardware.
        :param status: The current status associated an specific server hardware.

        :returns The status of corresponding server hardware.
        """
        if status:
            return const.METRIC_VALUE_PARSER[status]
        else:
            server_hardware = self.get_server_hardware(uuid)
            if server_hardware:
                status, timestamp = server_hardware['status'], server_hardware['modified']

                return const.METRIC_VALUE_PARSER[status], timestamp

        return None, None

    def get_server_hardware(self, uuid):
        """Call the function get_server_hardware encapsulate into run_by_retry function

        :param uuid: the id associated oneview server hardware resource.

        :return: a instance of a oneview server hardware resource.
        :raise LoginFailException if a client is no authenticated in Oneview Rest Api.
        :raises Exception if burst the max attempts.
        """
        return self._run_by_retry(self._get_server_hardware, uuid)

    def get_server_hardware_alerts(self, resource_uri, status):
        """Call the function get_server_hardware_alerts encapsulate into run_by_retry function

        :param resource_uri: the oneview uri resource
        :param status: the status associated with input resource.

        :return: a dict that contains all alerts associated with input resource.
        :raise LoginFailException if a client is no authenticated in Oneview Rest Api.
        :raises Exception if burst the max attempts.
        """
        return self._run_by_retry(self._get_server_hardware_alerts, resource_uri, status)

    def get_connection(self):
        """Call the function get_connection encapsulate into run_by_retry function

        :return: a connection to communicate with Oneview Rest Api
        :raise LoginFailException if a client is no authenticated in Oneview Rest Api.
        :raises Exception if burst the max attempts.
        """
        return self._run_by_retry(self._get_connection)

    def get_activity(self):
        """ Get a hpOneView activity model

        :return: a instance of activity model from hpOneView SDK.
        """
        con = self.get_connection()
        return activity(con)

    def get_security(self):
        """ Get a hpOneView security model

        :return: a instance of security model from hpOneView SDK.
        """
        con = self.get_connection()
        return security(con)

    def get_certificates(self):
        """ Get the path to SCMB certificates to open a connection with RabbitMQ

        :return: a dict that contains all certificates path
        """

        client_security = self.get_security()

        # Get a OneView certificates to connect on SCMB
        ca = client_security.get_cert_ca()
        kp = client_security.get_rabbitmq_kp()

        # Get pathfile certificates
        caroot = utils.save_file(self._directory, '/caroot.pem', ca)
        keydat = utils.save_file(self._directory, '/key.pem', kp['base64SSLKeyData'])
        client = utils.save_file(self._directory, '/client.pem', kp['base64SSLCertData'])

        return {
            "keyfile": keydat,
            "ca_certs": caroot,
            "certfile": client,
            "server_side": False,
            "cert_reqs": ssl.CERT_REQUIRED
        }

    def validate_certificates(self):
        """Call the function validate_certificates encapsulate into run_by_retry function

        :raise LoginFailException if a client is no authenticated in Oneview Rest Api.
        :raises Exception if burst the max attempts.
        """
        return self._run_by_retry(self._validate_certificates)

    def _get_server_hardware(self, uuid):
        """ Get a instance of a server hardware from oneview

        :param uuid: the id associated oneview server hardware resource.
        :return: a instance of a oneview server hardware resource.
        """
        client = OneViewClient({
            'ip': self._host,
            'credentials': {'userName': self._username, 'password': self._password}
        })
        try:
            return client.server_hardware.get(uuid)
        except HPOneViewException as hpex:
            if const.RESOURCE_NOT_FOUND in str(hpex):
                utils.print_log_message('Info', hpex.msg.replace('\n', ' '), LOG)
                return {}
            else:
                raise

    def _get_server_hardware_alerts(self, resource_uuid, status):
        """Get the alerts associated an Oneview resource when it is not OK

        :param resource_uuid: the server hardware uuid for the resource
        :param status: the status associated with input resource.

        :return: a dict that contains all alerts associated with input resource.
        """
        if status is None or status == const.METRIC_VALUE_PARSER['OK']:
            return {}

        act = self.get_activity()
        oneview_uri = const.ONEVIEW_URI_PREFIX + resource_uuid
        alerts = act.get_alerts(const.ALERT_BASE_URL + oneview_uri)

        meta_values = {}
        for alert in alerts:
            if len(meta_values) < const.MAX_VALUE_META_LEN:
                meta_values[alert['uri']] = self._host + '#/activity/r' + alert['uri']
            else:
                break

        return meta_values

    def _get_connection(self):
        """ Get a hpOneView SDK connection

        :return: a connection to communicate with Oneview Rest Api
        """
        con = connection(self._host)
        con.login({'userName': self._username, 'password': self._password})

        if con.get_eula_status():
            con.set_eula(supportAccess='no')

        return con

    def _validate_certificates(self):
        """ Validate the current SCMB certificates

        :return: None
        """
        try:
            client_security = self.get_security()
            client_security.gen_rabbitmq_self_signed_ca()
        except Exception as ex:
            if const.CERTIFICATE_VALID in str(ex):
                utils.print_log_message('Info', 'The certificate does not need to be validated.', LOG)
            else:
                raise ex

    def _run_by_retry(self, func, *args):
        """Function to manager Exceptions between Oneview Rest Api connection.

        :param func: A function that will be executed.
        :param args: A list of params to rum input function.

        :returns the input function output.
        :raise LoginFailException if a client is no authenticated in Oneview Rest Api.
        :raises Exception if burst the max attempts.
        """
        try:
            return utils.try_execute(func, self._max_attempt, 2000, *args)
        except HPOneViewException as hpex:
            if const.HTTP_ERROR_400 in str(hpex):
                utils.print_log_message('Error', const.HTTP_ERROR_400, LOG)
                raise HTTPFailException(const.HTTP_ERROR_400)

            elif const.LOGIN_FAILED in str(hpex):
                utils.print_log_message('Error', const.LOGIN_FAILED, LOG)
                raise LoginFailException(const.LOGIN_FAILED)

            else:
                msg = 'Unexpected error: %(message)s' % {'message': str(hpex)}
                utils.print_log_message('Error', msg, LOG)
                raise hpex
        except:
            raise
