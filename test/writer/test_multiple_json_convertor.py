#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest

import pandas as pd

from ingen.writer.json_writer.convertors.df_to_multiple_json_convertor import DFToMultipleJsonConvertor


class TestMultipleJSONConvertor(unittest.TestCase):
    def test_json_strings(self):
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['sachin', 'dhoni', 'kohli']
        })

        output_config = {
            'type': 'json_writer',
            'props': {
                'convertor': 'multiple',
                'convertor_props': {
                    'json_template': '{"id": <id>, "meta": "data", "name": <name>}'
                },
                'destination': 'file',
                'destination_props': {
                    'path': '../fake/file.json'
                }
            }
        }
        expected_json_strings = [
            '{"id": 1, "meta": "data", "name": sachin}',
            '{"id": 2, "meta": "data", "name": dhoni}',
            '{"id": 3, "meta": "data", "name": kohli}'
        ]
        convertor = DFToMultipleJsonConvertor()
        convertor_props = output_config.get('props').get('convertor_props')
        json_strings = convertor.convert(df, convertor_props)
        self.assertListEqual(expected_json_strings, json_strings)

    def test_missing_col(self):
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['sachin', 'dhoni', 'kohli']
        })
        output_config = {
            'type': 'json_writer',
            'props': {
                'convertor': 'multiple',
                'convertor_props': {
                    'json_template': "{'id': <id>, 'meta': 'data', 'name': <full_name>}"
                },
                'destination': 'file',
                'destination_props': {
                    'path': '../fake/file.json'
                }
            }
        }
        convertor = DFToMultipleJsonConvertor()
        convertor_props = output_config.get('props').get('convertor_props')

        with self.assertRaises(KeyError):
            json_strings = convertor.convert(df, convertor_props)


if __name__ == '__main__':
    unittest.main()
