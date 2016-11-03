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
This module provide the Initialize of the Monasca OneView Daemon
"""

from oneview_monasca.infrastructure.validations import InvalidConfigFileException
from oneview_monasca.shared.parse_command import ParseCommand
from oneview_monasca.application.daemon import Daemon
from oneview_monasca.shared import log as logging
from oneview_monasca.shared import utils

import os
import sys
import signal

LOG = logging.get_logger(__name__)


def main():
    """The main method that starts the daemon execution.

    :raises a KeyboardInterrupt if the user interrupts the execution via keyboard.
    :raises an Exception if something else goes wrong.
    """
    try:
        conf = ParseCommand().parse(sys.argv[1:])
        if conf:
            Daemon(conf).start()
    except KeyboardInterrupt:
        print("\nOneView Monasca Daemon stopped")
        sys.exit(130)
    except InvalidConfigFileException as confEx:
        print("\nInvalid config file input. OneView Monasca Daemon stopped")
        utils.print_log_message('Error', confEx, LOG)
        sys.exit(1)
    except Exception as ex:
        print("\nUnexpected error. OneView Monasca Daemon stopped")
        utils.print_log_message('Error', ex, LOG)
        os.kill(os.getpid(), signal.SIGTERM)


if __name__ == '__main__':
    main()
