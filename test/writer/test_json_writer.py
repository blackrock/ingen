#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from unittest.mock import Mock

import pandas as pd

from ingen.writer.json_writer.convertors.convertor_factory import get_json_convertor
from ingen.writer.json_writer.convertors.df_to_single_json_convertor import DFToSingleJsonConvertor
from ingen.writer.json_writer.destinations.destination_factory import get_json_destination
from ingen.writer.json_writer.destinations.file_destination import FileDestination
from ingen.writer.json_writer.json_writer import JSONWriter


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.df = pd.DataFrame({
            'name': ['Ramesh', 'Suresh', 'Jaya', 'Rekha'],
            'marks': [20, 40, 50, 30]
        })

        self.single_file_output_config = {
            'type': 'json_writer',
            'props': {
                'convertor': 'single',
                'convertor_props': {
                    'orient': 'records',
                    'indent': 4,
                    'column_details': {
                        'schema': [
                            {
                                'field_name': 'col_name',
                                'field_type': 'str'
                            }
                        ]
                    },
                    'resultant_columns': ['col_name']
                },
                'destination': 'file',
                'destination_props': {
                    'path': '../fake/file.json'
                }
            }
        }

    def test_correct_convertor_and_destination_is_called(self):
        mock_convertor_factory = Mock()
        mock_convertor = Mock()
        mock_convertor_factory.return_value = mock_convertor

        mock_json_strings = ["{'name': 'piyush', 'age': '26'}"]
        mock_convertor.convert.return_value = mock_json_strings

        mock_destination_factory = Mock()
        mock_destination = Mock()
        mock_destination_factory.return_value = mock_destination
        convertor_props = self.single_file_output_config.get('props').get('convertor_props')
        destination_props = self.single_file_output_config.get('props').get('destination_props')

        writer = JSONWriter(self.df, self.single_file_output_config.get('props'),
                            json_convertor_factory=mock_convertor_factory,
                            json_destination_factory=mock_destination_factory)
        writer.write()

        mock_convertor.convert.assert_called_with(self.df, convertor_props)
        mock_destination.handle.assert_called_with(mock_json_strings, destination_props)

    def test_json_writer_is_called_with_correct_args(self):
        no_destination_output_config = {
            'type': 'json_writer',
            'props': {
                'convertor': 'single',
                'convertor_props': {
                    'orient': 'records',
                    'indent': 4,
                    'column_details': {
                        'schema': [
                            {
                                'field_name': 'col_name',
                                'field_type': 'str'
                            }
                        ]
                    },
                    'resultant_columns': ['col_name']
                }
            }
        }
        with self.assertRaises(ValueError):
            writer = JSONWriter(self.df, no_destination_output_config.get('props'))

    def test_json_convertor_factory(self):
        convertor_name = 'single'
        convertor = get_json_convertor(convertor_name)
        self.assertIsInstance(convertor, DFToSingleJsonConvertor)

    def test_json_destination_factory(self):
        destination_name = 'file'
        destination = get_json_destination(destination_name)
        self.assertIsInstance(destination, FileDestination)


if __name__ == '__main__':
    unittest.main()
