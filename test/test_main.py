#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from unittest import mock
from unittest.mock import Mock, patch

from ingen.data_source.json_source import JsonSource
from ingen.main import *


class TestMain(unittest.TestCase):
    @patch('ingen.main.MetaDataParser')
    def test_metadata_parser(self, mock_metadata_parser):
        config_path = 'path/to/file'
        query_params = {}
        interfaces_list = None
        run_date = date.today()
        infile = None
        user_domain = None
        dynamic_data = None

        parser = Mock()
        parser.parse_metadata.return_value = []
        mock_metadata_parser.return_value = parser

        main(config_path, query_params, run_date, interfaces_list)

        mock_metadata_parser.assert_called_with(config_path, query_params, run_date, interfaces_list, infile,
                                                user_domain, dynamic_data)
        parser.parse_metadata.assert_called_once()

    @patch('ingen.main.MetaDataParser')
    def test_main_calls_generate(self, mock_metadata_parser):
        config_path = 'path/to/file'
        query_params = {}
        interfaces_list = None
        run_date = date.today()

        metadata1 = Mock()
        mock_source = Mock()
        metadata1.sources = [mock_source]
        parser = Mock()
        mock_run_config = Mock()
        mock_generator = Mock()
        parser.parse_metadata.return_value = [metadata1]
        parser.run_config = mock_run_config
        mock_run_config.generator.return_value = mock_generator
        mock_metadata_parser.return_value = parser

        main(config_path, query_params, run_date, interfaces_list)

        mock_generator.generate.assert_called_with(
            metadata1.name,
            metadata1.sources,
            metadata1.pre_processes,
            metadata1.columns,
            metadata1.output,
            metadata1.params,
            metadata1.validation_action
        )

    @patch('ingen.main.MetaDataParser')
    @patch('ingen.main.log')
    def test_main_catches_exception_and_system_exit(self, mock_logging, mock_metadata_parser):
        config_path = 'path/to/file'
        query_params = {}
        interfaces_list = None
        run_date = date.today()

        metadata1 = Mock()
        mock_source = Mock()
        metadata1.sources = [mock_source]
        parser = Mock()
        mock_run_config = Mock()
        mock_generator = Mock()
        mock_generator.generate.side_effect = Exception('Custom Exception')
        parser.parse_metadata.return_value = [metadata1]
        parser.run_config = mock_run_config
        mock_run_config.generator.return_value = mock_generator
        mock_metadata_parser.return_value = parser
        with self.assertRaises(SystemExit):
            main(config_path, query_params, run_date, interfaces_list)

        message = f"Failed to generate interface file for {metadata1.name} \n Custom Exception"
        mock_logging.error.assert_called_with(message)

    def test_query_params_arguments(self):
        arguments = ['file/to/metadata.yml', '--query_params', 'date=12/09/1995', 'table=position']
        parser = create_arg_parser()
        parsed_args = parser.parse_args(arguments)
        self.assertDictEqual({'date': '12/09/1995', 'table': 'position'}, parsed_args.query_params)
        self.assertEqual(arguments[0], parsed_args.config_path)

    def test_interfaces_params_arguments(self):
        arguments = ['file/to/metadata.yml', '12242020', '--interfaces', ['positions', 'account']]
        parser = create_arg_parser()
        parsed_args = parser.parse_args(arguments)
        self.assertEqual(['positions', 'account'], parsed_args.interfaces)

    @patch('ingen.main.create_arg_parser')
    @patch('ingen.main.main')
    def test_init(self, main_mock, parser_mock):
        parse = Mock()
        parser_mock.return_value = parse
        args = Mock()
        parse.parse_args.return_value = args
        init(args)
        main_mock.assert_called_with(args.config_path, args.query_params, args.run_date, args.interfaces, args.infile,
                                     args.user_domain)

    @patch('ingen.main.MetaDataParser')
    def test_process_json_with_dynamic_data(self, mock_metadata_parser):
        config_path = 'path/to/file'
        payload = '{"payload": {"id": "123"} }'

        metadata1 = Mock()
        mock_source = mock.MagicMock(spec=JsonSource)
        metadata1.sources = [mock_source]
        parser = Mock()
        mock_run_config = Mock()
        mock_generator = Mock()
        mock_interface = Mock()
        parser.parse_metadata.return_value = [metadata1]
        parser.run_config = mock_run_config
        mock_run_config.generator.return_value = mock_generator
        mock_generator.generate.return_value = mock_interface
        mock_metadata_parser.return_value = parser

        actual_interface = process_json(config_path, payload)

        mock_generator.generate.assert_called_with(
            metadata1.name,
            metadata1.sources,
            metadata1.pre_processes,
            metadata1.columns,
            metadata1.output,
            metadata1.params,
            metadata1.validation_action
        )
        self.assertEqual(mock_interface, actual_interface)


if __name__ == '__main__':
    unittest.main()
