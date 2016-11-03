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
from retrying import retry
from stevedore import driver
from ovm_serverlist.shared import log as logging
from ovm_serverlist.shared.exceptions import LoginFailException

LOG = logging.get_logger(__name__)


def print_log_message(log_type, message, log=LOG, debug=False):
    """Encapsulation of the logging message.

    :param log_type: the level of  logging that will be applied.
    :param message: the message to be presented into the logging.
    :param log: the log object from the class that call this method.
    :param debug: enable debug mode.
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


def load_class_by_alias(namespace, name):
    """Load class using stevedore alias

    :param namespace: namespace where the alias is defined
    :param name: alias name of the class to be loaded
    :returns class if calls can be loaded
    :raises ImportError if class cannot be loaded
    """
    try:
        message = 'Load class by alias: Namespace[%s], Name[%s].' % (namespace, name)
        print_log_message('Info', message)
        class_to_load = driver.DriverManager(
            namespace=namespace,
            name=name
        ).driver

    except RuntimeError:
        raise ImportError("Class not found.")

    return class_to_load


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
    @retry(wait_fixed=wait, stop_max_attempt_number=max_attempt,
           retry_on_exception=not_retry_if_login_fail)
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
            if max_attempt > 1:
                print_log_message('Info', " ---- Trying Again ---- ")
            raise

    # Executing the input function by retry decorator
    return execute()


def get_input(message):
    """
    Gets an input from the user.
    :param message: the message that indicates what the user should input
    :return: the user input
    """
    return input(message)
