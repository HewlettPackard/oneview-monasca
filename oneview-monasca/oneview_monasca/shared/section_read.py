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
Reads a section of a file.
"""

import configparser


class SectionRead:
    """Class that implements the reading of a section of a file.
    """
    def __init__(self, full_path_to_file, defaults={}):
        self._CONF = configparser.ConfigParser(defaults)
        self._CONF.readfp(open(full_path_to_file))

    def __getattr__(self, section):
        """Gets an attribute based on a section of a file.
        :param section: section to be analyzed.
        """
        result = Section(self._CONF.items(section), section)
        return result

    def __nonzero__(self):
        return True


class Section(object):
    """Class that represents a section of a file.
    """
    def __init__(self, cfg_section, section):
        self.__dict__ = dict(cfg_section)
        self.section = section

    def __getattribute__(self, *args, **kwargs):
        """Gets an attribute based on a section.
        :param args: arguments to match in the file.
        :param kwargs: TODO (documentation)
        """
        try:
            return object.__getattribute__(self, *args, **kwargs)
        except AttributeError:
            raise AttributeError("Missing required attribute '%s' on "
                                 "section '%s' " % (args[0], self.section))
