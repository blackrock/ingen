import unittest

import numpy as np
import pandas as pd

from ingen.pre_processor.merger import Merger


class TestDFMerger(unittest.TestCase):

    def test_merge_without_keys(self):
        dummy_data1 = {
            'id': ['1', '2', '6', '7', '8'],
            'accno': ['ABCD', 'EFGH', 'IJKL', 'MNOP', 'RSTU'],
            'name': ['JOEY', 'MONICA', 'ROSS', 'CHANDLER', 'RACHEL']}

        df1 = pd.DataFrame(dummy_data1, columns=['id', 'accno', 'name'])

        dummy_data2 = {
            'id': ['1', '2', '3', '4', '5', '7', '8', '9', '10', '11'],
            'cash': [12, 13, 14, 15, 16, 17, 15, 12, 13, 23]}

        df2 = pd.DataFrame(dummy_data2, columns=['id', 'cash'])

        expected_result = {
            'id': ['1', '2', '7', '8'],
            'accno': ['ABCD', 'EFGH', 'MNOP', 'RSTU'],
            'name': ['JOEY', 'MONICA', 'CHANDLER', 'RACHEL'],
            'cash': [12, 13, 17, 15]}

        result_df = pd.DataFrame(expected_result, columns=['id', 'accno', 'name', 'cash'])

        config = {'type': 'merge', 'source': 'source2'}
        merger = Merger()
        result = merger.execute(config, {'source1': df1, 'source2': df2}, df1)

        self.assertTrue(pd.DataFrame.equals(result_df, result))

    def test_left_outer_merge(self):
        dataframe1 = pd.DataFrame({
            'name': ['Payal', 'Pankaj', 'Pritam', 'Parth'],
            'marks': [88, 87, 90, 89]
        })
        dataframe2 = pd.DataFrame({
            'name': ['Payal', 'Pritam', 'Parth', 'Ajit'],
            'city': ['Pune', 'Ahmedabad', 'New York', 'Sydney']
        })
        expected_data = pd.DataFrame({
            'name': ['Payal', 'Pankaj', 'Pritam', 'Parth'],
            'marks': [88, 87, 90, 89],
            'city': ['Pune', np.NaN, 'Ahmedabad', 'New York']
        })
        config = {'type': 'merge',
                  'source': 'dataframe2',
                  'merge_type': 'left',
                  }

        merger = Merger()
        actual_data = merger.execute(config, {'dataframe1': dataframe1, 'dataframe2': dataframe2}, dataframe1)

        pd.testing.assert_frame_equal(expected_data, actual_data)

    def test_right_outer_merge(self):
        dataframe1 = pd.DataFrame({
            'name': ['Payal', 'Pankaj', 'Pritam', 'Parth'],
            'marks': [88, 87, 90, 89]
        })
        dataframe2 = pd.DataFrame({
            'name': ['Payal', 'Pritam', 'Parth', 'Ajit'],
            'city': ['Pune', 'Ahmedabad', 'New York', 'Sydney']
        })
        expected_data = pd.DataFrame({
            'name': ['Payal', 'Pritam', 'Parth', 'Ajit'],
            'marks': [88, 90, 89, np.NaN],
            'city': ['Pune', 'Ahmedabad', 'New York', 'Sydney']
        })
        config = {'type': 'merge',
                  'source': 'dataframe2',
                  'merge_type': 'right',
                  }

        merger = Merger()
        actual_data = merger.execute(config, {'dataframe2': dataframe2}, dataframe1)

        pd.testing.assert_frame_equal(expected_data, actual_data)

    def test_merge_with_different_column_names(self):
        dataframe1 = pd.DataFrame({
            'name': ['Payal', 'Pankaj', 'Pritam', 'Parth'],
            'marks': [88, 87, 90, 89]
        })
        dataframe2 = pd.DataFrame({
            'student_name': ['Payal', 'Pritam', 'Parth', 'Ajit'],
            'city': ['Pune', 'Ahmedabad', 'New York', 'Sydney']
        })
        expected_data = pd.DataFrame({
            'name': ['Payal', 'Pritam', 'Parth', np.NaN],
            'marks': [88, 90, 89, np.NaN],
            'student_name': ['Payal', 'Pritam', 'Parth', 'Ajit'],
            'city': ['Pune', 'Ahmedabad', 'New York', 'Sydney']
        })
        config = {'type': 'merge',
                  'source': 'dataframe2',
                  'merge_type': 'right',
                  'left_key': 'name',
                  'right_key': 'student_name'}

        merger = Merger()
        actual_data = merger.execute(config, {'dataframe2': dataframe2}, dataframe1)

        pd.testing.assert_frame_equal(expected_data, actual_data)

    def test_merge_on_intermediate_data(self):
        intermediate_data = pd.DataFrame({
            'name': ['Payal', 'Pankaj', 'Pritam', 'Parth'],
            'marks': [88, 87, 90, 89]
        })
        data_to_merge = pd.DataFrame({
            'name': ['Payal', 'Pritam', 'Parth', 'Ajit'],
            'city': ['Pune', 'Ahmedabad', 'New York', 'Sydney']
        })
        expected_data = pd.DataFrame({
            'name': ['Payal', 'Pritam', 'Parth', 'Ajit'],
            'marks': [88, 90, 89, np.NaN],
            'city': ['Pune', 'Ahmedabad', 'New York', 'Sydney']
        })
        config = {'type': 'merge',
                  'source': 'data_to_merge',
                  'merge_type': 'right'}

        merger = Merger()
        actual_data = merger.execute(config, {'data_to_merge': data_to_merge}, intermediate_data)

        pd.testing.assert_frame_equal(expected_data, actual_data)

    def test_missing_keys(self):
        dataframe1 = pd.DataFrame({
            'name': ['Payal', 'Pankaj', 'Pritam', 'Parth'],
            'marks': [88, 87, 90, 89]
        })
        dataframe2 = pd.DataFrame({
            'name': ['Payal', 'Pritam', 'Parth', 'Ajit'],
            'city': ['Pune', 'Ahmedabad', 'New York', 'Sydney']
        })

        left_key = 'not_present'
        right_key = 'name'

        config = {'type': 'merge',
                  'source': 'dataframe2',
                  'merge_type': 'right',
                  'left_key': left_key,
                  'right_key': right_key}

        merger = Merger()
        with self.assertRaisesRegex(KeyError, f"Column '{left_key}' not present in left dataframe"):
            merger.execute(config, {'dataframe2': dataframe2}, dataframe1)

    def test_missing_keys_right(self):
        dataframe1 = pd.DataFrame({
            'name': ['Payal', 'Pankaj', 'Pritam', 'Parth'],
            'marks': [88, 87, 90, 89]
        })
        dataframe2 = pd.DataFrame({
            'name': ['Payal', 'Pritam', 'Parth', 'Ajit'],
            'city': ['Pune', 'Ahmedabad', 'New York', 'Sydney']
        })

        right_key = 'not_present'
        left_key = 'name'

        config = {'type': 'merge',
                  'source': 'dataframe2',
                  'merge_type': 'right',
                  'left_key': left_key,
                  'right_key': right_key}

        merger = Merger()
        with self.assertRaisesRegex(KeyError, f"Column '{right_key}' not present in right dataframe"):
            merger.execute(config, {'dataframe2': dataframe2}, dataframe1)

    def test_merge_with_multiple_column_merge(self):
        dataframe1 = pd.DataFrame({
            'name': ['Payal', 'Pankaj', 'Parth', 'Pritam'],
            'marks': [88, 87, 90, 89]
        })
        dataframe2 = pd.DataFrame({
            'name': ['Payal', 'Pankaj', 'Parth'],
            'marks': [88, 87, 100],
            'city': ['Pune', 'Ahmedabad', 'New York']
        })
        expected_df = pd.DataFrame({
            'name': ['Payal', 'Pankaj', 'Parth', 'Pritam'],
            'marks': [88, 87, 90, 89],
            'city': ['Pune', 'Ahmedabad', np.NaN, np.NaN]
        })

        config = {'type': 'merge',
                  'source': 'data_to_merge',
                  'left_key': ['name', 'marks'],
                  'right_key': ['name', 'marks'],
                  'merge_type': 'left'}

        merger = Merger()
        actual_data = merger.execute(config, {'data_to_merge': dataframe2}, dataframe1)

        pd.testing.assert_frame_equal(expected_df, actual_data)


if __name__ == '__main__':
    unittest.main()
