import unittest
from unittest.mock import Mock, patch

from ingen.writer.writer import *


class TestWriter(unittest.TestCase):

    @patch('ingen.writer.old_json_writer.process_dataframe_columns_schema')
    def test_json_writer_valid_inputs(self, mock_process_dataframe_columns_schema):
        df = Mock()
        mock_to_json = Mock()
        mock_process_dataframe_columns_schema.return_value = mock_to_json
        output_type = 'json'
        props = {'delimiter': ',', 'path': '../output/accounts.json',
                 'config': {'orient': 'records', 'indent': 3,
                            'column_details': {'schema': [{'field_name': 'foo_id'}], 'resultant_columns': ['foo_id']},
                            }}
        print(props['config']['orient'])
        writer = OldJSONWriter(df=df, output_type=output_type, writer_props=props)
        writer.write()
        mock_process_dataframe_columns_schema.assert_called_once()
        mock_to_json.to_json.assert_called_with(path_or_buf=props['path'],
                                                orient=props['config']['orient'],
                                                indent=props['config']['indent'])


if __name__ == '__main__':
    unittest.main()
