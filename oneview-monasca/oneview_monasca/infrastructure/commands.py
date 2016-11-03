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


"""Generates the configuration file based on the user input.
"""

from oneview_monasca.shared import utils as utils
from oneview_monasca.shared import constants as const
from configparser import ConfigParser

import os
import getpass


def do_genconfig(args):
    """Generates the config file according to user input
    """

    print("========= DEFAULT ========")
    debug = utils.get_input(
        "Enable agent in debug mode [y/N]: ") or 'n'
    retry_interval = utils.get_input(
        "Type the polling interval in seconds for daemon to manage the nodes: ")
    batch_publishing_interval = utils.get_input(
        "Type the publishing interval in seconds for daemon to push the metrics: ")
    refresh_interval = utils.get_input(
        "Type the polling interval in seconds to get health status directly from OneView: ")
    scmb_certificate_dir = utils.get_input(
        "Type the certificates directory to register in OneView SCMB [/var/run/oneview-monasca]: ")
    auth_retry_limit = utils.get_input(
        "Type the maximum number of attempts to try authenticate in REST API: ")

    debug = 'false' if debug == 'n' else 'true'
    retry_interval = retry_interval if retry_interval else "300"
    refresh_interval = refresh_interval if refresh_interval else "180"
    batch_publishing_interval = batch_publishing_interval if batch_publishing_interval else "60"

    auth_retry_limit = auth_retry_limit if auth_retry_limit else "5"
    scmb_certificate_dir = scmb_certificate_dir if scmb_certificate_dir else "/var/run/oneview-monasca"

    scmb_certificate_dir = os.path.realpath(os.path.expanduser(scmb_certificate_dir))
    utils.makedirs(scmb_certificate_dir)

    print("========= Openstack =========")
    auth_url = utils.get_input("Type the Keystone url for authentication: ")
    auth_user = utils.get_input("Type the name of your OpenStack user: ")
    auth_password = getpass.getpass("Type the password for your OpenStack user: ")
    auth_tenant_name = utils.get_input("Type the tenant name that the OpenStack user will be authenticated: ")
    monasca_api_version = utils.get_input("Type a version of Monasca API that you want to use [2_0]: ")

    monasca_api_version = monasca_api_version if monasca_api_version else "2_0"

    print("========= OneView =========")
    oneview_manager_url = utils.get_input("Type the manager_url for the OneView services: ")
    oneview_username = utils.get_input("Type your OneView username: ")
    oneview_password = getpass.getpass("Type your OneView user's password: ")
    oneview_insecure = utils.get_input("Would you like to allow insecure connections to OneView? [Y/n]: ") or "Y"
    max_polling_attempts = utils.get_input("Max polling attempts OneView requests: ")
    tls_cacert_file = utils.get_input("Path to your CA OneView certificate file, if any: ")

    oneview_host = utils.extract_domain_from_service_url(oneview_manager_url)
    oneview_insecure = "true" if oneview_insecure.lower() == 'y' else "false"
    max_polling_attempts = max_polling_attempts if max_polling_attempts else "15"

    fault_tolerance_enable = False
    group_name = coordinator_url = None
    while True:
        create = utils.get_input("Would you like to enable fault tolerance in the agent? [Y/n] ") or 'y'

        if create.lower() == 'y':
            print("========= Tooz =========")

            group_name = utils.get_input("The group name for tooz configuration: ")
            coordinator_url = utils.get_input("The coordinator url for tooz configuration: ")
            fault_tolerance_enable = True
            break
        elif create.lower() == 'n':
            break
        else:
            print("Invalid option.\n")

    config_drivers = {}
    try:
        names = utils.list_names_driver(const.NAMESPACE_DISCOVERY_NODES, log=False)
    except Exception as ex:
        print('\nCannot load installed drivers - Error caused by %s\n' % str(ex))
        names = []

    for name in names:
        try:
            conf = utils.load_class_by_alias(
                const.NAMESPACE_DISCOVERY_NODES, name, log=False).genconfig()

            config_drivers[name.split('_')[-1]] = conf
        except Exception as ex:
            print('\nCannot generating config file session to driver: %s - Error caused by %s\n' % (name, str(ex)))

    # Write Configuration file #
    config = ConfigParser()
    config.set("DEFAULT", "debug", debug)
    config.set("DEFAULT", "retry_interval", retry_interval)
    config.set("DEFAULT", "periodic_refresh_interval", refresh_interval)
    config.set("DEFAULT", "batch_publishing_interval", batch_publishing_interval)

    config.set("DEFAULT", "auth_retry_limit", auth_retry_limit)
    config.set("DEFAULT", "scmb_certificate_dir", scmb_certificate_dir)

    if fault_tolerance_enable:
        config.add_section("tooz")
        config.set("tooz", "group_name", group_name)
        config.set("tooz", "coordinator_url", coordinator_url)

    config.add_section("openstack")
    config.set("openstack", "auth_url", auth_url)
    config.set("openstack", "auth_user", auth_user)
    config.set("openstack", "auth_password", auth_password)
    config.set("openstack", "auth_tenant_name", auth_tenant_name)
    config.set("openstack", "monasca_api_version", monasca_api_version)

    config.add_section("oneview")
    config.set("oneview", "host", oneview_host)
    config.set("oneview", "manager_url", oneview_manager_url)
    config.set("oneview", "username", oneview_username)
    config.set("oneview", "password", oneview_password)
    config.set("oneview", "allow_insecure_connections", oneview_insecure)
    config.set("oneview", "max_polling_attempts", max_polling_attempts)
    config.set("oneview", "tls_cacert_file", tls_cacert_file)

    for driver in config_drivers:
        config.add_section(driver)
        for option, value in config_drivers[driver].items():
            config.set(driver, option, value)

    if not args.config_file:
        args.config_file = '~' + os.path.sep + 'oneview_monasca.conf'

    filename = utils.get_input(
        "Type the path of the new configuration file [%s]: " % args.config_file) or args.config_file
    full_filename = os.path.realpath(os.path.expanduser(filename))

    config_dir = os.path.dirname(full_filename)
    utils.makedirs(config_dir)

    with open(full_filename, 'w') as configfile:
        config.write(configfile)
        print("======\nFile created successfully on '%s'!\n======" % filename)
