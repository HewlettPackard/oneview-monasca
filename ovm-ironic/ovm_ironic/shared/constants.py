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
Default module that contains all constants used in this project
"""

''' LOG '''
# The format to output log
FORMATTER_LOG = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

''' Manager Ironic '''
# The metric name
METRIC_NAME = 'oneview.server_hardware'
# The service name
SERVICE_NAME = 'ironic'
# Template to represent a valid dimension
TEMPLATE_DIMENSIONS = {
    'resource_id': '',
    'server_hardware_uuid': '',
    'service': ''
}
# Supported drivers to interest nodes
SUPPORTED_DRIVERS = ["agent_pxe_oneview", "iscsi_pxe_oneview", "fake_oneview"]
# API version of Ironic Client
API_VERSION = 1
