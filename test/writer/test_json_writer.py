#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pytest
import pandas as pd

from ingen.writer.json_writer.convertors.convertor_factory import get_json_convertor
from ingen.writer.json_writer.convertors.df_to_single_json_convertor import DFToSingleJsonConvertor
from ingen.writer.json_writer.destinations.destination_factory import get_json_destination
from ingen.writer.json_writer.destinations.file_destination import FileDestination
from ingen.writer.json_writer.json_writer import JSONWriter


class TestJSONWriter:
    def setup_method(self):
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
        class MockConvertor:
            def __init__(self):
                self.convert_calls = []
            
            def convert(self, df, props):
                self.convert_calls.append((df, props))
                return ["{'name': 'piyush', 'age': '26'}"]

        class MockDestination:
            def __init__(self):
                self.handle_calls = []
            
            def handle(self, json_strings, props):
                self.handle_calls.append((json_strings, props))

        mock_convertor = MockConvertor()
        mock_destination = MockDestination()

        def mock_convertor_factory(name, *args):
            return mock_convertor

        def mock_destination_factory(name, *args):
            return mock_destination

        convertor_props = self.single_file_output_config.get('props').get('convertor_props')
        destination_props = self.single_file_output_config.get('props').get('destination_props')

        writer = JSONWriter(self.df, self.single_file_output_config.get('props'),
                            json_convertor_factory=mock_convertor_factory,
                            json_destination_factory=mock_destination_factory)
        writer.write()

        assert mock_convertor.convert_calls == [(self.df, convertor_props)]
        assert mock_destination.handle_calls == [(["{'name': 'piyush', 'age': '26'}"], destination_props)]

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
        with pytest.raises(ValueError):
            writer = JSONWriter(self.df, no_destination_output_config.get('props'))

    def test_json_convertor_factory(self):
        convertor_name = 'single'
        convertor = get_json_convertor(convertor_name)
        assert isinstance(convertor, DFToSingleJsonConvertor)

    def test_json_destination_factory(self):
        destination_name = 'file'
        destination = get_json_destination(destination_name)
        assert isinstance(destination, FileDestination)