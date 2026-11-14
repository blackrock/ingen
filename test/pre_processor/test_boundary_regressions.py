import unittest

import pandas as pd

from ingen.pre_processor.aggregator import Aggregator
from ingen.pre_processor.melt import Melt
from ingen.pre_processor.outer_join import OuterJoin


class TestPreProcessorBoundaries(unittest.TestCase):
    def test_aggregation_only_reduces_configured_column(self):
        data = pd.DataFrame({'fund': ['a', 'a', 'b'], 'quantity': [2, 3, 4],
                             'price': [10, 20, 30]})
        result = Aggregator().execute(
            {'type': 'aggregate', 'groupby': {'cols': ['fund']},
             'agg': {'operation': 'sum', 'col': 'quantity'}}, {}, data)
        expected = pd.DataFrame({'fund': ['a', 'b'], 'quantity': [5, 4]})
        pd.testing.assert_frame_equal(result, expected)

    def test_melt_defaults_to_all_columns_without_include_keys(self):
        data = pd.DataFrame({'a': [1], 'b': [2]})
        result = Melt().execute(
            {'source': ['input'], 'key_column': 'key', 'value_column': 'value'},
            {'input': data}, None)
        pd.testing.assert_frame_equal(
            result, pd.DataFrame({'key': ['a', 'b'], 'value': [1, 2]}))

    def test_outer_join_accepts_composite_keys(self):
        left = pd.DataFrame({'fund': ['a', 'a'], 'id': [1, 2], 'left': ['x', 'y']})
        right = pd.DataFrame({'fund': ['a', 'b'], 'id': [1, 2], 'right': ['z', 'w']})
        result = OuterJoin().execute(
            {'source': 'right', 'left_key': ['fund', 'id'], 'right_key': ['fund', 'id']},
            {'right': right}, left)
        expected = pd.DataFrame({'fund': ['a', 'a', 'b'], 'id': [1, 2, 2],
                                 'left': ['x', 'y', ''], 'right': ['z', '', 'w']})
        pd.testing.assert_frame_equal(result, expected)
