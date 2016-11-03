# -*- coding: utf-8 -*-

# Copyright 2016 Hewlett Packard Enterprise Development LP
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
Tests of ParseCommand module.
"""

from base import TestBase
from oneview_monasca.shared import parse_command

import mock
import argparse


class TestParseCommand(TestBase):
    """ This class test the pase_command module from oneview_monasca.shared.
    """
    def setUp(self):
        """Setting up the tests.
        """
        super(TestParseCommand, self).setUp()

    def tearDown(self):
        """Tearing down the tests.
        """
        super(TestParseCommand, self).tearDown()

    # this method tests the constant version
    def test_version(self):
        """ Test cases regarding the value of the constant VERSION from this module.
        Test flow:
                >>> Test if the constant value is equal to itself;
                >>> Test if the constant value is equal to its supposed value;
                >>> Test if the constant value is not empty
                >>> Test if the constant value is not equal to a different value of the supposed one; and,
                >>> Test if the constant value is not None.
        """
        # testing if it is equals to it self
        self.assertEqual(parse_command.VERSION, parse_command.VERSION)
        # testing if it is equals to its supposed value
        self.assertEqual(parse_command.VERSION, '1.0')
        # testing if it is not empty
        self.assertNotEqual(parse_command.VERSION, '')
        # testing if it is not equals to aleatory version
        self.assertNotEqual(parse_command.VERSION, '-1.0')
        # testing if it is not null
        self.assertNotEqual(parse_command.VERSION, None)

    # this method tests the __init__
    def test_init(self):
        """ Test cases regarding the __init__ method of the ParseCommand class
        """
        # creating the object
        p = parse_command.ParseCommand()
        # testing if the attribute parser is null
        self.assertEqual(p.parser, None)
        # testing if the attribute subcommands is null
        self.assertEqual(p.subcommands, None)

    # this method tests the get_base_parser static method
    def test_get_base_parser(self):
        """ Test cases regarding the get_base_parser method of the ParseCommand class
        Test flow:
                >>> Call the static method and store its return in a parser variable;
                >>> Test if the parser variable is equal to itself;
                >>> Test if the parser variable is not empty
                >>> Test if the parser variable is not equal to an aleatory value;
                >>> Test if the type of the parser variable is equal to the supposed one;
                >>> Call the method for the second time and store its return in a new parser variable; and,
                >>> Test if the values of both parsers are equal.
        """
        # calling the method
        parser = parse_command.ParseCommand.get_base_parser()
        # testing if its return is equals to it self
        self.assertEqual(parser, parser)
        # testing if its return is not empty
        self.assertNotEqual(parser, '')
        # testing if its return is not aleatory value
        self.assertNotEqual(parser, 'test')
        # testing the type of its return
        self.assertEqual(type(parser), argparse.ArgumentParser)
        # testing if the returns of two calls are equal
        parser2 = parse_command.ParseCommand.get_base_parser()
        self.assertEqual(parser.prog, parser2.prog)
        self.assertEqual(parser.usage, parser2.usage)
        self.assertEqual(parser.description, parser2.description)
        self.assertEqual(parser.version, parser2.version)
        self.assertEqual(parser.formatter_class, parser2.formatter_class)
        self.assertEqual(parser.conflict_handler, parser2.conflict_handler)
        self.assertEqual(parser.add_help, parser2.add_help)

    # this method tests the get_subcommand_parser method
    def test_get_subcommand_parser(self):
        """ Test cases regarding the get_subcommand_parser method of the ParseCommand class
        Test flow:
                >>> Create an object of the class and store it in a variable;
                >>> Call the method and store its return in a parser object;
                >>> Test if the parser value is equal to itself;
                >>> Test if the parser value is not empty;
                >>> Test if the parser value is not equal to an alleatory value;
                >>> Test if the type of the parser variable is equal to the supposed one;
                >>> Call the method for the second time and store its return in a new parser variable; and,
                >>> Test if the values of both parsers are equal.
        """
        # creating the object
        p = parse_command.ParseCommand()
        # calling the method
        parser = p.get_base_parser()
        # testing if its return is equals to it self
        self.assertEqual(parser, parser)
        # testing if its return is not empty
        self.assertNotEqual(parser, '')
        # testing if its return is not aleatory value
        self.assertNotEqual(parser, 'test')
        # testing the type of its return
        self.assertEqual(type(parser), argparse.ArgumentParser)
        # testing if the returns of two calls are equal
        parser2 = p.get_base_parser()
        self.assertEqual(parser.prog, parser2.prog)
        self.assertEqual(parser.usage, parser2.usage)
        self.assertEqual(parser.description, parser2.description)
        self.assertEqual(parser.version, parser2.version)
        self.assertEqual(parser.formatter_class, parser2.formatter_class)
        self.assertEqual(parser.conflict_handler, parser2.conflict_handler)
        self.assertEqual(parser.add_help, parser2.add_help)

    # this method tests the do_help method
    def test_do_help(self):
        """ Test cases regarding the do_help method of the ParseCommand class
        Test flow:
                >>> Create an object of the class and store it in a variable;
                >>> Initialize the parser variable from the parser_command object by calling the get_subcommand method
                >>> with the "help genconfig" command as parameter;
                >>> Call the method and store its return in the h variable;
                >>> Test if the h variable value is None;
                >>> Test if the method executes without raising an exception when it receives a known command as
                >>> parameter; and
                >>> Test if the method raises an excepetion when it receiver an unknown command as parameter.
        """

        # creating the object
        p = parse_command.ParseCommand()
        p.parser = p.get_subcommand_parser()
        # calling the method
        h = p.do_help('help genconfig')
        # testing if method output is null
        self.assertEqual(h, None)
        # testing if exception is not raised when subcommand is known
        raised = False
        try:
            p.do_help('help genconfig')
        except:
            raised = True
        self.assertFalse(raised, 'Exception raised')
        # testing if an exception is raised when subcommand is unknown
        self.assertRaises(Exception, p.do_help('help test'))

    # this method tests the do_help method
    def test_define_commands_from_module(self):
        """ Test cases regarding the define_commands_from_module method of the ParseCommand class
        Test flow:
                >>> Create two objects of the class and store it in variables (p1 and p2);
                >>> Call the method get_base_parser once for each object and store the returns in variables (parser 1
                and parser2);
                >>> Call the method add_subparsers with the parameter metavar='<subcommand>' once for each object and
                store the return in variables (subparsers1 and subparsers2);
                >>> For each object, call the method with the paraneters subparserX, None and None;
                >>> Test if after the method execution, the values of the subparsers variables are equal; and,
                >>> Test if the method raises an exception when is called twice by the same object.
        """
        # creating the object
        p1 = parse_command.ParseCommand()
        p2 = parse_command.ParseCommand()
        parser1 = p1.get_base_parser()
        parser2 = p2.get_base_parser()
        subparsers1 = parser1.add_subparsers(metavar='<subcommand>')
        subparsers2 = parser2.add_subparsers(metavar='<subcommand>')
        # testing if after calling the method for two subparsers, they are still equals
        p1.define_commands_from_module(subparsers1, None, None)
        p2.define_commands_from_module(subparsers2, None, None)
        self.assertEquals(subparsers1.option_strings, subparsers2.option_strings)
        self.assertEquals(subparsers1.dest, subparsers2.dest)
        self.assertEquals(subparsers1.nargs, subparsers2.nargs)
        self.assertEquals(subparsers1.const, subparsers2.const)
        self.assertEquals(subparsers1.default, subparsers2.default)
        self.assertEquals(subparsers1.type, subparsers2.type)
        self.assertEquals(subparsers1.choices, subparsers2.choices)
        self.assertEquals(subparsers1.help, subparsers2.help)
        self.assertEquals(subparsers1.metavar, subparsers2.metavar)
        # testing if an exception is raised when the method is called twice for the same parser
        self.assertRaises(Exception, p1.define_commands_from_module(subparsers1, None, None))

    # this method tests the enhance_parser method
    def test_enhance_parser(self):
        """ Test cases regarding the enhance_parser method of the ParseCommand class
        Test flow:
                >>> Create an empty list;
                >>> Creates an object of the class and stores it in a variable;
                >>> Calls the method get_base_parser and stores its return in a parser variable;
                >>> Calls the method add_subparsers from the parser with the parameter
                metavar='<subcommand>' and stores its return as a subparsers variable;
                >>> Calls the method add_parser from the subparsers variable with the parameter
                'help genconfig' and stores its return as a subparser variable;
                >>> Adds the subparser to the list under the "help" index; and,
                >>> Tests if the method raises an exception when it receives the subparsers and the
                list as parameters.
        """
        # creating objects
        cmd_mapper = {}
        p = parse_command.ParseCommand()
        parser = p.get_base_parser()
        subparsers = parser.add_subparsers(metavar='<subcommand>')
        subparser = subparsers.add_parser('help genconfig')
        cmd_mapper['help'] = subparser
        # testing if an exception is raised when the method is called if wrong parameters
        self.assertRaises(Exception, p.enhance_parser(subparsers, cmd_mapper))

    @mock.patch('oneview_monasca.shared.utils.get_input')
    def test_parse(self, mock_input):
        """Test case regarding the parse method of the ParseCommand class.
        Test flow:
            >>> Creates an object of the class and stores it in a variable;
            >>> Calls the method with an empty parameter; and,
            >>> Test if it raised an exception.
        """
        mock_input.return_value = 'n'
        p = parse_command.ParseCommand()

        raised = False
        try:
            p.parse('')
        except:
            raised = True

        self.assertTrue(raised)
