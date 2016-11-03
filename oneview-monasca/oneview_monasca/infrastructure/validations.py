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
This module is auxiliary function to check agent configuration file correctness
"""

from oneview_client import client
from ironicclient import client as ironic
from monascaclient import client as monclient, ksclient
from oneview_monasca.shared.section_read import SectionRead
from oneview_monasca.shared import log as logging
from oneview_monasca.shared import utils

import os
import re
import sys
import argparse
import traceback

LOG = logging.get_logger(__name__)


# TODO (diegoadolfo): Try move this class to exceptions module
class InvalidConfigFileException(Exception):
    """ The exception class that is raised when input config file is not valid.
    """
    def __init__(self, message=None):
        Exception.__init__(self, message)


def validate_config(config_file, shell=False):
    """ Function to test the correctness of agent configuration file

    :param config_file: The agent configuration file
    :param shell: Flag to identify if this script is running by shell
    """
    if config_file is None:
        raise InvalidConfigFileException("CONFIG FILE cannot be reachable.")

    # Type consistency: verify if fields are corrected filled with the specific expected type of data
    if False in map(_is_positive_int,
                    [config_file.DEFAULT.retry_interval, config_file.DEFAULT.auth_retry_limit,
                     config_file.DEFAULT.periodic_refresh_interval, config_file.DEFAULT.batch_publishing_interval]):
        raise InvalidConfigFileException("CONFIG FILE has any inconsistency type error, check it.")

    # Addresses: check every address to see if they are valid and they really lead to the correct machine
    if False in map(_is_url,
                    [config_file.oneview.manager_url, config_file.openstack.auth_url]):
        raise InvalidConfigFileException("CONFIG FILE has any invalid url, check it.")

    _chk_oneview_credentials(
        config_file.oneview.manager_url,
        config_file.oneview.username, config_file.oneview.password
    )

    _chk_openstack_credentials(
        config_file.openstack.auth_url, config_file.openstack.auth_user,
        config_file.openstack.auth_password, config_file.openstack.auth_tenant_name,
        config_file.openstack.monasca_api_version
    )

    try:
        _chk_ironic_credentials(
            config_file.ironic.auth_url, config_file.ironic.admin_user,
            config_file.ironic.admin_password, config_file.ironic.admin_tenant_name,
            config_file.ironic.insecure, config_file.ironic.ironic_api_version
        )
    except InvalidConfigFileException:
        raise
    except Exception:
        pass

    if shell:
        print('CONFIG FILE is valid, starting daemon application')
    else:
        utils.print_log_message('Info', 'CONFIG FILE is valid, starting daemon application', LOG)


def _is_positive_int(value):
    """Check if a string is a positive integer

    :param value: A string that will be checked.
    """
    if value[0] == '-':
        return False

    if value[0] == '+':
        return value[1:].isdigit()
    else:
        return value.isdigit()


def _is_url(value):
    """Check if a string is a valid url

    :param value: A string that will be checked.
    """
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, value)


def _chk_ironic_credentials(auth_url, username, password, tenant_name, insecure, api_version):
    """Check if ironic credentials is valid

    :param auth_url: The ironic auth url
    :param username: The cloud-admin username
    :param password: The cloud-admin password
    :param tenant_name: The cloud-admin project name
    :param insecure: Flag to allow insecure requests
    :param api_version: The ironic api version
    """
    kwargs = {
        'os_username': username,
        'os_password': password,
        'os_auth_url': auth_url,
        'os_tenant_name': tenant_name,
        'os_ironic_api_version': api_version
    }
    if insecure.lower() == 'true':
        kwargs['insecure'] = True

    try:
        ironic.get_client(1, **kwargs)
    except:
        raise InvalidConfigFileException(
            "Impossible created a connection with ironic services, check the CONFIG FILE")


def _chk_openstack_credentials(auth_url, username, password, project_name, api_version):
    """Check if openstack credentials is valid

    :param auth_url: The keystone auth url
    :param username: The cloud-admin username
    :param password: The cloud-admin password
    :param project_name: The cloud-admin project name
    :param api_version: The monasca api version
    """
    try:
        ks = ksclient.KSClient(auth_url=auth_url, username=username, password=password, project_name=project_name)
        monclient.Client(api_version, ks.monasca_url, token=ks.token)
    except:
        raise InvalidConfigFileException(
            "Impossible created a connection with openstack services, check the CONFIG FILE")


def _chk_oneview_credentials(manager_url, username, password, max_attempt=20, ca_file='', insecure='True'):
    """Check if oneview credentials is valid

    :param manager_url: The oneview appliance host
    :param username: The administrator username
    :param password: The administrator password
    """
    kwargs = {
        'manager_url': manager_url,
        'username': username,
        'password': password,
        'max_polling_attempts': max_attempt,
    }

    if ca_file:
        kwargs['tls_cacert_file'] = ca_file
    if insecure.lower() == 'true':
        kwargs['allow_insecure_connections'] = True

    try:
        client.ClientV2(**kwargs)
    except:
        raise InvalidConfigFileException(
            "Impossible created a connection with oneview services, check the CONFIG FILE")


def main():
    """
    The main method
    """
    parser = argparse.ArgumentParser(
        add_help=True,
        formatter_class=argparse.RawTextHelpFormatter,
        description='''This script will be validate a user input config file to run Monasca-Oneviewd'''
    )
    # Global Arguments
    parser.add_argument(
        '-c', '--config-file',
        dest='config_file', required=False,
        help='''Default path to configuration file'''
    )

    args = parser.parse_args()
    full_path_to_file = os.path.realpath(os.path.expanduser(args.config_file))

    config_file = SectionRead(full_path_to_file)
    try:
        validate_config(config_file, True)
    except:
        traceback.print_exc()


if __name__ == '__main__':
    main()
    sys.exit(0)
