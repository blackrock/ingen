#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from ingen.writer.writer import *


class TestWriter:

    def test_json_writer_valid_inputs(self, monkeypatch):
        class MockDataFrame:
            def __init__(self):
                self.to_json_calls = []
            
            def to_json(self, path_or_buf, orient, indent):
                self.to_json_calls.append((path_or_buf, orient, indent))

        mock_df = MockDataFrame()
        
        def mock_process_dataframe_columns_schema(*args, **kwargs):
            return mock_df
        
        monkeypatch.setattr("ingen.writer.old_json_writer.process_dataframe_columns_schema", mock_process_dataframe_columns_schema)
        
        output_type = 'json'
        props = {'delimiter': ',', 'path': '../output/accounts.json',
                 'config': {'orient': 'records', 'indent': 3,
                            'column_details': {'schema': [{'field_name': 'foo_id'}], 'resultant_columns': ['foo_id']},
                            }}
        print(props['config']['orient'])
        writer = OldJSONWriter(df=mock_df, output_type=output_type, writer_props=props)
        writer.write()
        
        assert mock_df.to_json_calls == [(props['path'], props['config']['orient'], props['config']['indent'])]