#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import json
import unittest
from unittest.mock import Mock, patch

import pandas as pd

from ingen.data_source.json_source import JsonSource
from ingen.generators.interface_generator import InterfaceGenerator


class TestInterfaceGenerator(unittest.TestCase):
    def test_read(self):
        mock_df = pd.DataFrame({'data': [1, 2, 3]})
        source = Mock()
        source.fetch.return_value = mock_df
        sources = [source]

        generator = InterfaceGenerator()
        data = generator.read(sources)
        self.assertTrue(pd.DataFrame.equals(mock_df, data[source.id]))

    def test_pre_processor(self):
        config = [{'type': 'merge', 'source': ['source1', 'source2'], 'key_column': 'id'}]
        data = pd.DataFrame({'name': ['Jon Snow', 'Arya']})
        mock_pre_processor = Mock()
        mock_processor = Mock()

        mock_pre_processor.return_value = mock_processor
        generator = InterfaceGenerator(pre_processor=mock_pre_processor)
        generator.pre_process(config, data)

        mock_pre_processor.assert_called_with(config, data)
        mock_processor.pre_process.assert_called_once()

    def test_format(self):
        df = pd.DataFrame({'ticker': ['ABC', 'ZXY'], 'price': [123, 45.56]})
        columns = [
            {
                'src_col_name': 'ticker'
            },
            {
                'src_col_name': 'price',
                'formatters':
                    [
                        {
                            'type': 'float',
                            'format': '${:,.2f}'
                        }
                    ]
            }
        ]
        expected_df = pd.DataFrame({'ticker': ['ABC', 'ZXY'], 'price': ['$123.00', '$45.56']})
        generator = InterfaceGenerator()
        generator.format(df, columns, {})
        self.assertTrue(pd.DataFrame.equals(expected_df, df))

    def test_write(self):
        data = pd.DataFrame({'name': ['Jon Snow', 'Arya']})
        destination = {
            'type': 'file',
            'props': {
                'path': 'path/to/file',
                'delimiter': ','
            }
        }

        mock_interface_writer = Mock()
        mock_writer = Mock()
        mock_interface_writer.return_value = mock_writer
        generator = InterfaceGenerator(writer=mock_interface_writer)
        generator.write(data, destination, {})

        mock_interface_writer.assert_called_with(data, destination['type'], destination['props'], {})
        mock_writer.write.assert_called_once()

    def test_validate(self):
        columns = [
            {
                'src_col_name': 'ACCOUNT_ID',
                'validations': [
                    {
                        'type': 'expect_column_values_to_not_be_null',
                        'severity': 'critical'
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['8262400', '8262410', '8262420', '8262430', None],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        dataframe_expected = pd.DataFrame({
            'ACCOUNT_ID': ['8262400', '8262410', '8262420', '8262430'],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201']
        })

        generator = InterfaceGenerator()
        dataframe_actual, _ = generator.validate(dataframe, columns)
        self.assertTrue(pd.DataFrame.equals(dataframe_actual, dataframe_expected))

    def test_validate_when_only_source_given(self):
        source = Mock()
        source.fetch.return_value = pd.DataFrame()
        source.fetch_validations.return_value = [{}]
        source._src = {
            'id': 'test_id',
            'type': 'file',
            'file_type': 'delimited_file',
            'src_data_checks': [
                {
                    'src_col_name': 'ACCOUNT_ID',
                    'validations': [
                        {
                            'type': 'expect_column_values_to_not_be_null',
                            'severity': 'warning'
                        }
                    ]
                }
            ]
        }
        generator = InterfaceGenerator()
        sources = [source]

        validated_df, validation_summary = generator.validate(pd.DataFrame(), [], sources=sources)
        pd.testing.assert_frame_equal(validated_df, pd.DataFrame())
        self.assertTrue(len(validation_summary) == 1)

    def test_notify_when_email_given(self):
        params_map = {'query_params': None, 'run_date': 20221112}
        validation_action = {
            'send_email': ['a.b@c.com']
        }
        validation_summaries = {'test': 'body'}

        generator = InterfaceGenerator()

        with patch('smtplib.SMTP', autospec=True) as mock_smtp:
            generator.notify(params_map, validation_action, validation_summaries)
            mock_smtp.assert_called_once()

    @patch('ingen.validation.notification.email_attributes')
    def test_notify_when_email_not_given(self, mock):
        params_map = {'query_params': None, 'run_date': 20221112}
        validation_action = {}
        validation_summaries = dict()

        generator = InterfaceGenerator()

        generator.notify(params_map, validation_action, validation_summaries)
        mock.assert_not_called()

    def test_generate_when_validation_only(self):
        json_tbl = """{
                "id": "here",
                "attr1": "there",
                "attr2": "anywhere"
        }"""
        json_data = '{ "obj1":' + json_tbl + '}'
        source_info = {
            'id': 'obj1',
            'type': 'json'
        }
        json_source = JsonSource(source_info, json_data)

        interface_name = 'json_interface'
        sources = [json_source]
        pre_processes = None
        columns = [{'src_col_name': 'id',
                    'validations': [{'type': 'expect_column_values_to_not_be_null', 'severity': 'warning'}]},
                   {'src_col_name': 'attr1',
                    'validations': [{'type': 'expect_column_values_to_not_be_null', 'severity': 'warning'}]},
                   {'src_col_name': 'attr2',
                    'validations': [{'type': 'expect_column_values_to_not_be_null', 'severity': 'warning'}]}]
        destination = {'type': None, 'props': {}}
        params = {'query_params': None, 'run_date': None, 'infile': None}
        validation_action = None

        generator = InterfaceGenerator()

        interface = generator.generate(interface_name, sources, pre_processes, columns, destination, params,
                                       validation_action)
        self.assertEqual(json.loads(json_tbl), json.loads(interface))


if __name__ == '__main__':
    unittest.main()
