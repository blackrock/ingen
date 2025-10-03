#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import json
import pytest

import pandas as pd

from ingen.data_source.json_source import JsonSource
from ingen.generators.interface_generator import InterfaceGenerator


class TestInterfaceGenerator:
    def test_read(self):
        mock_df = pd.DataFrame({'data': [1, 2, 3]})
        
        class SourceStub:
            def __init__(self):
                self.id = 'test_id'
            
            def fetch(self):
                return mock_df
        
        source = SourceStub()
        sources = [source]

        generator = InterfaceGenerator()
        data = generator.read(sources)
        pd.testing.assert_frame_equal(mock_df, data[source.id])

    def test_pre_processor(self):
        config = [{'type': 'merge', 'source': ['source1', 'source2'], 'key_column': 'id'}]
        data = pd.DataFrame({'name': ['Jon Snow', 'Arya']})
        
        class ProcessorStub:
            def __init__(self):
                self.pre_process_calls = 0
            
            def pre_process(self):
                self.pre_process_calls += 1
        
        class PreProcessorStub:
            def __init__(self):
                self.call_args = []
                self.processor = ProcessorStub()
            
            def __call__(self, config, data):
                self.call_args.append((config, data))
                return self.processor
        
        pre_processor_stub = PreProcessorStub()
        generator = InterfaceGenerator(pre_processor=pre_processor_stub)
        generator.pre_process(config, data)

        assert (config, data) in pre_processor_stub.call_args
        assert pre_processor_stub.processor.pre_process_calls == 1

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
        pd.testing.assert_frame_equal(expected_df, df)

    def test_write(self):
        data = pd.DataFrame({'name': ['Jon Snow', 'Arya']})
        destination = {
            'type': 'file',
            'props': {
                'path': 'path/to/file',
                'delimiter': ','
            }
        }

        class WriterStub:
            def __init__(self):
                self.write_calls = 0
            
            def write(self):
                self.write_calls += 1
        
        class InterfaceWriterStub:
            def __init__(self):
                self.call_args = []
                self.writer = WriterStub()
            
            def __call__(self, data, dest_type, props, params):
                self.call_args.append((data, dest_type, props, params))
                return self.writer
        
        interface_writer_stub = InterfaceWriterStub()
        generator = InterfaceGenerator(writer=interface_writer_stub)
        generator.write(data, destination, {})

        expected_args = (data, destination['type'], destination['props'], {})
        assert expected_args in interface_writer_stub.call_args
        assert interface_writer_stub.writer.write_calls == 1

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
        pd.testing.assert_frame_equal(dataframe_actual, dataframe_expected)

    def test_validate_when_only_source_given(self):
        class SourceStub:
            def __init__(self):
                self.id = 'test_id'
                self._src = {
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
            
            def fetch(self):
                return pd.DataFrame()
            
            def fetch_validations(self):
                return [{}]
        
        source = SourceStub()
        generator = InterfaceGenerator()
        sources = [source]

        validated_df, validation_summary = generator.validate(pd.DataFrame(), [], sources=sources)
        pd.testing.assert_frame_equal(validated_df, pd.DataFrame())
        assert len(validation_summary) == 1

    def test_notify_when_email_given(self, monkeypatch):
        params_map = {'query_params': None, 'run_date': 20221112}
        validation_action = {
            'send_email': ['a.b@c.com']
        }
        validation_summaries = {'test': 'body'}

        class SMTPStub:
            def __init__(self, *args, **kwargs):
                self.call_count = 0
                self.send_message_calls = []
            
            def __enter__(self):
                self.call_count += 1
                return self
            
            def __exit__(self, *args):
                pass
            
            def send_message(self, message):
                self.send_message_calls.append(message)
            
            def starttls(self):
                pass
            
            def login(self, user, password):
                pass

        smtp_calls = []
        def smtp_constructor(*args, **kwargs):
            smtp_calls.append((args, kwargs))
            return SMTPStub(*args, **kwargs)

        monkeypatch.setattr('smtplib.SMTP', smtp_constructor)
        
        generator = InterfaceGenerator()
        generator.notify(params_map, validation_action, validation_summaries)
        
        assert len(smtp_calls) == 1

    def test_notify_when_email_not_given(self, monkeypatch):
        params_map = {'query_params': None, 'run_date': 20221112}
        validation_action = {}
        validation_summaries = dict()

        email_attributes_calls = []
        def email_attributes_stub(*args, **kwargs):
            email_attributes_calls.append((args, kwargs))

        monkeypatch.setattr('ingen.validation.notification.email_attributes', email_attributes_stub)
        
        generator = InterfaceGenerator()
        generator.notify(params_map, validation_action, validation_summaries)
        
        assert len(email_attributes_calls) == 0

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
        post_processes = None
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
                                       validation_action, post_processes)
        assert json.loads(json_tbl) == json.loads(interface)
