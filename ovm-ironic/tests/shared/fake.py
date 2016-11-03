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


from ovm_ironic.driver.base import DiscoveryNodeSubscriber

import uuid


class FakeNodeIronic(object):
    """A fake class to make possible to test the get_node_list method
    """
    __dict__ = {'uuid': uuid.uuid4()}

    def __init__(self):
        self.driver = 'fake_oneview'
        self.driver_info = {'server_hardware_uri': '/server-hardware/' + uuid.uuid4().__str__()}

    @staticmethod
    def fake_get_node_list():
        """Gets a collection of nodes of the ironic client.

        :returns the collection of nodes.
        """
        return [FakeNodeIronic()]


class FakeComponentListener(DiscoveryNodeSubscriber):
    """Simulates a component listener to makes possible the test of the load_plugin_get_nodes method.
    """
    def __init__(self):
        DiscoveryNodeSubscriber.__init__(self)
        self.nodes = set()

    def available(self, nodes):
        """Turns nodes available.
        :param nodes: nodes collection to be available.
        """
        self.nodes.update(nodes)

    def unavailable(self, nodes):
        """Turns nodes unavailable.
        :param nodes: nodes collection to be unavailable.
        """
        self.nodes.difference_update(nodes)
