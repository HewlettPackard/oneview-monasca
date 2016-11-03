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
Representation of a Metric.
"""


class Metric(object):
    """This class represents a Metric.

    :param name: A string, the name of metric.
    :param dimensions: A dict, the dimensions of metric.
    """
    def __init__(self, name, dimensions={}):
        self.name = name
        self.dimensions = dimensions

    def __eq__(self, other):
        if isinstance(other, Metric):
            return self.name == other.name and \
                self.dimensions.items() == other.dimensions.items()
        return False

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return 'name[%s], dimensions[%s]' % (
            self.name,
            self.dimensions
        )
