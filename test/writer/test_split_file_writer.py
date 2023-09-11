#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from unittest.mock import patch

import pandas as pd

from ingen.writer.split_file_writer import SplitFileWriter


class TestSplitFileWriter(unittest.TestCase):
    def setUp(self):
        dummy_data1 = {
            'id': ['1', '2', '6', '7', '8'],
            'Feature1': ['ABC', 'XYZ', 'ABC', 'XYZ', 'ABC'],
            'Feature2': ['L', 'N', 'P', 'R', 'T']}
        self.df1 = pd.DataFrame(dummy_data1, columns=['id', 'Feature1', 'Feature2'])
        self.writer_props = [{'col': 'Feature1', 'value': 'ABC', 'type': 'delimited_file',
                              'props': {'header': {'type': 'delimited_result_header'}, 'delimiter': ',',
                                        'path': 'path/to/file/name_val1$date(%d%m%Y).csv'}},
                             {'col': 'Feature1', 'value': 'XYZ', 'type': 'delimited_file',
                              'props': {'header': {'type': 'delimited_result_header'}, 'delimiter': ',',
                                        'path': 'path/to/file/name_val2$date(%d%m%Y).csv'}}]

        self.writer = SplitFileWriter(self.df1, 'splitted_file', self.writer_props, {})

        expected_result1 = {
            'id': ['1', '6', '8'],
            'Feature1': ['ABC', 'ABC', 'ABC'],
            'Feature2': ['L', 'P', 'T']}
        self.expected_df1 = pd.DataFrame(expected_result1, columns=['id', 'Feature1', 'Feature2'])

        expected_result2 = {
            'id': ['2', '7'],
            'Feature1': ['XYZ', 'XYZ'],
            'Feature2': ['N', 'R']}
        self.expected_df2 = pd.DataFrame(expected_result2, columns=['id', 'Feature1', 'Feature2'])

    def test_get_filtered_results(self):
        result = self.writer.get_filtered_results('Feature1', 'ABC')
        self.assertTrue(pd.DataFrame.equals(self.expected_df1.reset_index(drop=True), result.reset_index(drop=True)))

    @patch('ingen.writer.split_file_writer.InterfaceWriter', autospec=True)
    def test_write(self, writer_mock):
        self.writer.write()
        pd.testing.assert_frame_equal(
            writer_mock.call_args[0][0],
            self.expected_df2.reset_index(drop=True)
        )


if __name__ == '__main__':
    unittest.main()
