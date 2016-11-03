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
Generates LOGs for actions.
"""

from ovm_serverlist.shared import constants as const

import logging
import sys

# Register loggers
LOGGERS = {}


def _get_handler():
    """
    A simple handler to the standard output.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(const.FORMATTER_LOG)
    )

    return handler


def get_logger(name):
    """
    Create a logger configuration.

    Usage::

        >>> import log
        >>> LOG = log.get_logger(__name__)
        >>> LOG.info(...)

    :param name: The class name.
    :rtype: A :class:`Logger <Logger>`
    """
    if name not in LOGGERS:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(_get_handler())
        LOGGERS[name] = logger

    return LOGGERS[name]
