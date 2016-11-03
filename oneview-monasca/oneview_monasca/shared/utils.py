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
Gathers useful methods for the whole system.
"""

from builtins import input
from oneview_monasca.shared.exceptions import LoginFailException
from oneview_monasca.shared import log as logging
from stevedore import extension
from datetime import datetime
from stevedore import driver
from retrying import retry

import os
import re
import pytz
import time
import tzlocal
import urlparse

LOG = logging.get_logger(__name__)


def print_log_message(log_type, message, log=LOG, debug=False):
    """Encapsulation of the logging message.

    :param log_type: the level of  logging that will be applied.
    :param message: the message to be presented into the logging.
    :param log: the log object from class that call this method.
    :param debug: flag to enable debug mode.
    :raises ValueError if the type of logging is invalid.
    """
    log_type = log_type.lower().strip()
    if log_type == 'debug' and debug:
        log.debug(message)
    elif log_type == 'info':
        log.info(message)
    elif log_type == 'error':
        log.error(message)
    elif log_type == 'warn':
        log.warn(message)
    elif log_type != 'debug':
        raise ValueError('Invalid log type: ' + log_type + '.')


def extract_domain_from_service_url(url):
    """Extracts the domain of a service url.

    :param url: the url to be extracted.
    :raises Exception if the received url has an invalid format.
    :returns the domain of the service url.
    """
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not re.match(regex, url):
        print_log_message('Error', 'Invalid URL input')
        raise Exception('Invalid URL input')
    else:
        return urlparse.urlparse(url).hostname


def makedirs(path, mode=0o777):
    """Creates a directory if it does not exist.
    :param path: path to the deserted directory.
    :param mode: the permission that a directory will be created.
    :raises OSError if the directory path is invalid.
    """

    if not path:
        raise OSError("Not a valid directory path")
    elif path[0] != os.path.sep and path[0] != '~':
        path = os.path.expanduser('~') + os.path.sep + path

    _makedirs(path, mode)


def _makedirs(path, mode=0o777):
    """Creates a directory if it does not exist.

    :param path: path to the deserted directory.
    :param mode: the permission that a directory will be created.
    :raises OSError if there is no permission to create the file.
    :returns None if the directory already exists.
    """
    if not path or os.path.exists(path):
        return

    head, tail = os.path.split(path)
    _makedirs(head, mode)

    try:
        os.makedirs(path, mode)
    except OSError as ex:
        message = 'OSError: %(errno)d, %(error)s, %(file)s. Permission denied to create the certificates directory.' % {
            'errno': ex.errno, 'error': ex.strerror, 'file': ex.filename
        }
        print_log_message('Error', message)
        raise


def save_file(directory, filename, certificate):
    """Saves a file with a certificate.
    :param directory: name of the directory where the file should be saved.
    :param filename: name of the file to be saved.
    :param certificate: certificate that should be written in the file.
    :returns the path to the saved file
    """
    if not os.path.exists(directory):
        makedirs(directory)

    pathfile = directory + filename

    with open(pathfile, 'w+') as f:
        f.write(certificate)
    return pathfile


def extract_oneview_uuid(oneview_uri):
    """Function to extract the uuid associated to OneView resource

    :param oneview_uri: The url with the uuid from the OneView resource
    :return: The uuid for the OneView resource
    """
    ov_uuid = oneview_uri.split('/')[-1]
    return ov_uuid


def load_class_by_alias(namespace, name, invoke_args=(), invoke_on_load=False, log=True):
    """Load class using stevedore alias.

    :param namespace: A string, namespace where the alias is defined.
    :param invoke_args: An object, the configuration to driver.
    :param name: A string, alias name of the class to be loaded.
    :param invoke_on_load: A boolean, if should invoke on load.
    :param log: enable log message
    :returns class if calls can be loaded.
    :raises ImportError if class cannot be loaded.
    """
    try:
        if log:
            message = 'Load class by alias: Namespace[%s], Name[%s].' % (namespace, name)
            print_log_message('Info', message)

        class_to_load = driver.DriverManager(
            namespace=namespace,
            name=name,
            invoke_args=invoke_args,
            invoke_on_load=invoke_on_load
        ).driver

    except RuntimeError:
        raise ImportError("Class not found.")

    return class_to_load


def list_names_driver(namespace, log=True):
    """Get a list of the names from namespace.

    :param namespace: namespace where the alias is defined.
    :param log: enable log message
    :returns list of names to the namespace.
    :raises Exception if any error.
    """
    try:
        if log:
            print_log_message('Info', 'Get names by Namespace[%s].' % namespace)

        ext = extension.ExtensionManager(namespace=namespace)
        return ext.names()
    except RuntimeError:
        raise Exception("Error list names.")


def parse_timestamp(str_timestamp, format='%Y-%m-%dT%H:%M:%S.%fZ'):
    """Parses a time stamp.

    :param str_timestamp: a string, the timestamp.
    :param format: a string, the default is date timezone.
    :returns the parsed time stamp in millis seconds.
    """
    local_tz = tzlocal.get_localzone()
    date_time = datetime.strptime(str_timestamp, format)
    date_time = date_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
    timestamp = time.mktime(date_time.timetuple()) + date_time.microsecond / 1E6

    return int(timestamp * 1000)


def not_retry_if_login_fail(exception):
    """Function to check if a LoginFailException occurs.

    :param exception: Some exception class
    :return: True if the input exception not is a instance of LoginFailException
    """
    return not isinstance(exception, LoginFailException)


def try_execute(func, max_attempt, wait, *args):
    """Function that trying to execute another function max_attempt times.

        :param func: A function that will be executed.
        :param max_attempt: The number max of attempts to execute input function.
        :param wait: The time (in milliseconds) between each attempt of execute input function.
        :param args: A list of params to rum input function.

        :returns the input function output.
        :raises Exception if burst the max attempts.
    """
    @retry(wait_fixed=wait, stop_max_attempt_number=max_attempt, retry_on_exception=not_retry_if_login_fail)
    def execute():
        """ Auxiliary function to use retry decorator.

        :return: the input function output.
        :raises: Exception if burst the max attempts.
        """
        try:
            return func(*args)
        except LoginFailException:
            raise
        except:
            print_log_message('Info', " ---- Trying Again ---- ")
            raise

    # Executing the input function by retry decorator
    return execute()


class SingletonType(type):
    """A simply type that has only one interesting inhabitant.
    """
    def __call__(cls, *args, **kwargs):
        """Calls the class.
        """
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(
                SingletonType, cls).__call__(*args, **kwargs)
            return cls.__instance


def arg(*args, **kwargs):
    """Decorator for CLI args.

    Example:

    >>> @arg("name", help="Name of the new entity")
    ... def entity_create(args):
    ...     pass
    """
    def _decorator(func):
        """ Auxiliary function to use decorator for CLI args.

        :param func: A function that will be executed.
        :return: A function decorator
        """
        add_arg(func, *args, **kwargs)
        return func
    return _decorator


def add_arg(func, *args, **kwargs):
    """Bind CLI arguments to a shell.py `do_foo` function."""

    if not hasattr(func, 'arguments'):
        func.arguments = []

    # NOTE(sip): avoid dips that can occur when the module is shared across
    # tests.
    if (args, kwargs) not in func.arguments:
        # Because of the semantics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        func.arguments.insert(0, (args, kwargs))


def extract_metric_names(metrics):
    """ Receive metrics to extract only the names
    and return these names in a list.

    :param metrics: Metrics to be processed.
    """
    names = []
    for metric in metrics:
        names.append(metric.name)

    return names


def log_actions(node, action, debug=False, log=LOG):
    """ This method send logs when a node is discovered or removed.

    :param node: Node that was discovered or removed.
    :param action: String representing the action.
    :param log: the log object from class that call this method.
    :param debug: flag to enable debug mode.
    """
    message_debug = 'Node %s: %s with metrics: %s' % (
        action,
        node.server_hardware_uuid,
        node.metrics
    )
    print_log_message('Debug', message_debug, log, debug)

    message_info = 'Node %s: %s with metrics: %s' % (
        action,
        node.server_hardware_uuid,
        extract_metric_names(node.metrics)
    )
    print_log_message('Info', message_info, log)


def get_input(message):
    """
    Gets an input from the user.
    :param message: the message that indicates what the user should input
    :return: the user input
    """
    return input(message)
