import unittest

import pandas as pd
from ingen.pre_processor.outer_join import OuterJoin


class TestOuterJoin(unittest.TestCase):

    def setUp(self):
        self.outer_join = OuterJoin()
        self.left_data = pd.DataFrame({
            'id1': [1, 2, 3],
            'value': ['A', 'B', 'C']
        })
        self.right_data = pd.DataFrame({
            'id': [1, 2, 4],
            'value': ['B', 'C', 'D']
        })

    def test_outer_join_success(self):
        """Test successful outer join with matching, left-only and right-only rows
        """

        config = {
            'source': 'test-users',
            'left_key': 'id1',
            'right_key': 'id'
        }

        sources_data = {'test-users': self.right_data}

        result = self.outer_join.execute(config, sources_data, self.left_data)

        self.assertEqual(len(result), 4)
        result_ids = [x for x in result['id1'].tolist() if x != '']
        result_id_second = [x for x in result['id'].tolist() if x != '']
        self.assertIn(1.0, result_ids)
        self.assertIn(2.0, result_ids)
        self.assertIn(3.0, result_ids)
        self.assertIn(4.0, result_id_second)


    def test_outer_join_missing_left_key(self):
        """Test outer join when left key is missing
        """
        left_data = {
            'id': [1, 2, 3],
            'value': ['A', 'B', 'C']
        }
        right_data = {
            'id': [2, 3, 4],
            'value': ['B', 'C', 'D']
        }
        left_df = pd.DataFrame(left_data)
        right_df = pd.DataFrame(right_data)

        config = {
            'source': 'right',
            'left_key': 'id',
            'right_key': 'id'
        }

        result = self.outer_join.execute(config, {'right': right_df}, left_df)

        expected_data = {
            'id': [1, 2, 3, 4],
            'value_x': ['A', 'B', 'C', ''],
            'value_y': ['', 'B', 'C', 'D']
        }
        expected_df = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(result, expected_df)