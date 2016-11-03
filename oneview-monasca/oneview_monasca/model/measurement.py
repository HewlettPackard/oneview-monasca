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
This module represent a measurement object that ManagerMonasca
will use.
"""

import time


class Measurement(object):
    """
    This class represents the measurement that will be used by
    ManagerMonasca to extract all information and create a metric
    to send to Monasca.

    :param name: (string(255), required) - The name of the metric.
    :param value: (float, required) - Value of the metric. Values with base-10
    exponents greater than 126 or less than -130 are truncated.
    :param dimensions: ({string(255): string(255)}, optional) - A dictionary
    consisting of (key, value) pairs used to uniquely identify a metric.
    :param value_meta: ({string(255): string}(2048), optional) - A dictionary
    consisting of (key, value) pairs used to add information about the value.
    Value_meta key value combinations must be 2048 characters or less
    including '{"":""}' 7 characters total from every json string.
    """
    def __init__(self, name, value, dimensions={}, value_meta={}):
        self.name = name
        self.value = value
        self.timestamp = time.time() * 1000
        self.dimensions = dimensions
        self.value_meta = value_meta

    def __eq__(self, other):
        """Method to compare Measurement objects """
        if isinstance(other, Measurement):
            return self.value == other.value and \
                self.dimensions.items() == other.dimensions.items() and \
                self.value_meta.items() == other.value_meta.items()
        return False
