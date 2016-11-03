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

"""Command-line interface to the Monasca OneView Daemon.
"""

from __future__ import print_function

from oneview_monasca.infrastructure.commands import do_genconfig
from oneview_monasca.shared.section_read import SectionRead
from oneview_monasca.infrastructure import commands as config
from oneview_monasca.infrastructure import validations
from oneview_monasca.shared import constants as const
from oneview_monasca.shared import utils
from builtins import input

import argparse
import os

VERSION = '1.0'

COMMAND_MODULES = [config]


class ParseCommand(object):
    """Class that implements the command-line interface to the Monasca OneView Daemon.
    """
    def __init__(self):
        super(ParseCommand, self).__init__()
        self.parser = None
        self.subcommands = None

    @staticmethod
    def get_base_parser():
        """Gets the base parser of the Monasca OneView Daemon.
        """
        epilog = 'See "{app_name} --help COMMAND for help on a specific command.'.format(
            app_name=const.APPLICATION_NAME
        )

        parser = argparse.ArgumentParser(
            prog=const.APPLICATION_NAME,
            description=__doc__.strip(),
            epilog=epilog,
            add_help=False,
            formatter_class=HelpFormatter,
        )

        # Global arguments
        parser.add_argument('-v', '--version', action='version',
                            version=VERSION)
        parser.add_argument('-h', '--help', action='help',
                            help=argparse.SUPPRESS)
        parser.add_argument('-c', '--config-file',
                            help='Default path to configuration file')

        return parser

    def get_subcommand_parser(self):
        """Gets the subcommand parser ot the Monasca OneView Daemon.
        """
        parser = self.get_base_parser()
        self.subcommands = {}

        subparsers = parser.add_subparsers(metavar='<subcommand>')
        self.enhance_parser(subparsers, self.subcommands)
        self.define_commands_from_module(subparsers, self, self.subcommands)
        return parser

    @utils.arg('command', metavar='<subcommand>', nargs='?', help='Display help for <subcommand>')
    def do_help(self, args):
        """Displays a help about this program or one of its subcommands.

        :param args: name of the program or subcommands.
        """
        if getattr(args, 'command', None):
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise Exception("'%s' is not a valid subcommand" % args.command)
        else:
            self.parser.print_help()

    def define_commands_from_module(self, subparsers, command_module, cmd_mapper):
        """Adds *do_* methods in a module and add as node_discoverer into a subparsers.

        :param subparsers: subparser collection.
        :param command_module: name of the module where the command is defined.
        :param cmd_mapper: TO DO
        """
        for method_name in (a for a in dir(command_module) if a.startswith('do_')):
            # Commands should be hypen-separated instead of underscores.
            command = method_name[3:].replace('_', '-')
            callback = getattr(command_module, method_name)
            self.define_command(subparsers, command, callback, cmd_mapper)

    def enhance_parser(self, subparsers, cmd_mapper):
        """Enhances a parser.

        :param subparsers: collection of parsers.
        :param cmd_mapper: TODO (documentation)
        """
        for command_module in COMMAND_MODULES:
            self.define_commands_from_module(subparsers, command_module, cmd_mapper)

    @staticmethod
    def define_command(subparsers, command, callback, cmd_mapper):
        """Define a command in the subparsers collection.

        :param subparsers: subparsers collection where the command will go.
        :param command: command name.
        :param callback: function that will be used to process the command.
        :param cmd_mapper: TODO (documentation)
        """

        desc = callback.__doc__ or ''
        help = desc.strip().split('\n')[0]
        arguments = getattr(callback, 'arguments', [])

        subparser = subparsers.add_parser(
            command,
            help=help,
            description=desc,
            add_help=False,
            formatter_class=HelpFormatter
        )
        subparser.add_argument('-h', '--help', action='help', help=argparse.SUPPRESS)
        cmd_mapper[command] = subparser

        for (args, kwargs) in arguments:
            subparser.add_argument(*args, **kwargs)

        subparser.set_defaults(func=callback)

    def parse(self, argv):
        """Parses an argument.
        :param argv: name of the argument.
        """
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        subcommand_parser = self.get_subcommand_parser()
        self.parser = subcommand_parser

        if len(argv) == 0 or '-c' in argv or '--config-file' in argv:
            config_file = self.get_configuration(options)
            validations.validate_config(config_file)
            return config_file

        args = subcommand_parser.parse_args(argv)
        args.func(args)

    @staticmethod
    def get_configuration(options):
        """Gets a configuration based on given options.

        :param options: collection of options names.
        """
        file_name = options.config_file

        if file_name:
            full_path_to_file = os.path.realpath(os.path.expanduser(file_name))
            return SectionRead(full_path_to_file)
        else:
            while True:
                create = utils.get_input("Config file not found. "
                                         "Would you like to create one now? [Y/n]") or 'y'

                if create.lower() == 'y':
                    do_genconfig(options)
                    # Loading new config file
                    full_path_to_file = os.path.realpath(os.path.expanduser(file_name))
                    return SectionRead(full_path_to_file)
                elif create.lower() == 'n':
                    return None
                else:
                    print("Invalid option.\n")


class HelpFormatter(argparse.HelpFormatter):
    """Intermediate class to HelpFormatter.
    :param argparser.HelpFormatter: performs the text formatting.
    """

    def start_section(self, heading):
        """Formats a section to begin with upper case.
        :param heading: section to be formatted
        """
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(HelpFormatter, self).start_section(heading)
