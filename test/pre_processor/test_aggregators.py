#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pandas as pd
from pandas.core.groupby.generic import DataFrameGroupBy

from ingen.pre_processor.aggregators import *


class TestAggregators:
    def test_group_by(self):
        config = {'cols': ['acc', 'cusip']}

        dummy_data1 = {
            'acc': ['abcd', 'abcd', 'abcd', 'abcd', 'xyz', 'xyz', 'xyz', 'xyz'],
            'cusip': ['ABC', 'ABC', 'DEF', 'DEF', 'GHI', 'GHI', 'JKL', 'JKL'],
            'quantity': [2, 2, 2, 2, 2, 2, 2, 2]}

        df1 = pd.DataFrame(dummy_data1, columns=['acc', 'cusip', 'quantity'])
        result = groupby(config, df1)
        assert isinstance(result, DataFrameGroupBy)

    def test_agg(self):
        config = {'operation': 'sum', 'col': 'quantity'}
        dummy_data1 = {
            'acc': ['abcd', 'abcd', 'abcd', 'abcd', 'xyz', 'xyz', 'xyz', 'xyz'],
            'cusip': ['ABC', 'ABC', 'DEF', 'DEF', 'GHI', 'GHI', 'JKL', 'JKL'],
            'quantity': [2, 2, 2, 2, 2, 2, 2, 2]}

        df1 = pd.DataFrame(dummy_data1, columns=['acc', 'cusip', 'quantity'])

        grouped = df1.groupby(['acc', 'cusip'])
        expected_result = grouped.agg('sum', 'quantity')
        result = agg(config, grouped)

        pd.testing.assert_frame_equal(expected_result, result)

    def test_get_aggregator(self):
        aggregator_type = 'groupby'
        assert get_aggregator(aggregator_type) == groupby

        aggregator_type = 'agg'
        assert get_aggregator(aggregator_type) == agg

    def custom_aggregator(config, data):
        return data

    def test_add_aggregator(self):
        aggregator_type = 'cust'
        custom_aggregator_func = self.custom_aggregator
        add_aggregator(aggregator_type, custom_aggregator_func)

        assert get_aggregator(aggregator_type) == custom_aggregator_func