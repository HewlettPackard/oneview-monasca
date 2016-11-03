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

""" Manages the Monasca Component """

from monascaclient import client as monclient, ksclient
from oneview_monasca.manager.abstract_manager_monasca import AbstractManagerMonasca
from oneview_monasca.shared import log as logging
from oneview_monasca.shared import utils

import monascaclient.exc as exc

LOG = logging.get_logger(__name__)


class ManagerMonasca(AbstractManagerMonasca):
    """ The Monasca Manager """

    def __init__(self, auth_url, username, password, project_name, api_version, debug=False):
        super(ManagerMonasca, self).__init__()

        utils.print_log_message('Info', 'Initialize Monasca Manager', LOG)

        self.debug = debug
        self.auth_url = auth_url
        self.username = username
        self.password = password
        self.project_name = project_name
        self.api_version = api_version

    def _get_monasca_client(self):
        """Provide a Monasca client according a configuration file

        :returns: Monasca client.
        """
        message = "Using OpenStack credentials specified in the configuration file to get Monasca Client"
        utils.print_log_message('Debug', message, LOG, self.debug)

        # Authenticate to Keystone
        ks = ksclient.KSClient(
            auth_url=self.auth_url,
            username=self.username,
            password=self.password,
            project_name=self.project_name
        )
        # Monasca Client
        monasca_client = monclient.Client(
            self.api_version, ks.monasca_url, token=ks.token
        )
        return monasca_client

    def send_metrics(self, measurements):
        """ Update a list of metric dictionary  measurements to be in the
        Metric format that Monasca allow and sends them in one request.

        :param measurements: A list of Measurement objects to send to Monasca.
        """
        utils.print_log_message('Debug', 'Send Metric - method send_metrics', LOG, self.debug)
        monasca_metric_list = []

        for measure in measurements:
            new_metric = dict()
            new_metric['name'] = measure.name
            new_metric['value'] = measure.value
            new_metric['timestamp'] = measure.timestamp
            new_metric['dimensions'] = measure.dimensions
            new_metric['value_meta'] = measure.value_meta
            monasca_metric_list.append(new_metric)

        batch_metrics = {'jsonbody': monasca_metric_list}
        try:
            monasca_client = self._get_monasca_client()
            monasca_client.metrics.create(**batch_metrics)
        except exc.HTTPException as httpex:
            utils.print_log_message('Error', httpex.message, LOG)
        except Exception as ex:
            utils.print_log_message('Error', ex.message, LOG)
            raise

        utils.print_log_message('Info', 'Finished send metric - method send_metrics', LOG)
