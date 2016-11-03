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
Representation of a Node, an OneView resource associated to many metrics'.
"""


class Node(object):
    """This class represents a OneView resource associated to many metrics.

    :param server_hardware_uuid: A string, the UUID from the Oneview resource.
    :param metrics: A set, the metrics to the server hardware.
    """
    def __init__(self, server_hardware_uuid, metrics=set()):
        self.server_hardware_uuid = server_hardware_uuid
        self.metrics = metrics

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.server_hardware_uuid == other.server_hardware_uuid and \
                self.metrics == other.metrics
        return False

    def __hash__(self):
        return hash(self.server_hardware_uuid)

    def __repr__(self):
        return 'server_hardware_uuid[%s], metrics[%s]' % (
            self.server_hardware_uuid,
            self.metrics
        )
