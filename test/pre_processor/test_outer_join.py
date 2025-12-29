from ingen.pre_processor.outer_join import OuterJoin


class TestOuterJoin:

    def setup(self):
        self.outer_join = OuterJoin()

    def test_outer_join_success(self):
        """Test successful outer join with matching, left-only and right-only rows
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