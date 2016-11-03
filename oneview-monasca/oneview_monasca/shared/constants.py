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
Global constants used in whole project
"""


''' APPLICATION '''
APPLICATION_NAME = 'monasca_oneviewd'

''' EventBUS '''
# The namespace to drivers of node discovery.
NAMESPACE_DISCOVERY_NODES = 'node_discovery.driver'

''' METRICS '''
METRIC_NAME = "oneview.node_status"

'''' MANAGER ONEVIEW '''
# Map with possibles status form the server hardware
METRIC_VALUE_PARSER = {
    "OK": 0,
    "Disabled": 1,
    "Critical": 2,
    "Warning": 3,
    "Unknown": 4
}
MAX_VALUE_META_LEN = 13
ONEVIEW_URI_PREFIX = '/rest/server-hardware/'

''' LOG '''
# The format to output log
FORMATTER_LOG = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

'''COORDINATOR'''
# A prefix name to the id of each coordinator created by tooz.
PREFIX_ID_COORD = b'oneviewd'
# Time to send a signal to inform that the coordinator is alive
HEARTBEAT_INTERVAL = 1

''' SCMB LISTENER '''
# The SCMB protocol name.
EXCHANGE_NAME = "scmb"
# The default routing key the listener all server hardware updates.
ROUTING_KEY = "scmb.server-hardware.Updated.#"
# The host to connect Pika and RabbitMQ.
MB_PORT = 5671

''' ONEVIEW MANAGER '''
# The base url to get a OneView alert.
ALERT_BASE_URL = 'Active' + "'&filter=resourceUri='"
# The message to invalid login
LOGIN_FAILED = 'Invalid username or password or directory.'
# The message if certificate is still valid
CERTIFICATE_VALID = 'The existing certificate is still valid'
# Error 400
HTTP_ERROR_400 = 'response: 400'
# Resource not found in oneview
RESOURCE_NOT_FOUND = 'Resource not found'
