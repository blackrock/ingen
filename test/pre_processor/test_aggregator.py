#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest

import pandas as pd

from ingen.pre_processor.aggregator import Aggregator


class TestAggregator(unittest.TestCase):
    def test_execute_function(self):
        config = {'type': 'aggregate', 'groupby': {'cols': ['acc', 'cusip']},
                  'agg': {'operation': 'sum', 'col': 'quantity'}}

        dummy_data1 = {
            'acc': ['abcd', 'abcd', 'abcd', 'abcd', 'xyz', 'xyz', 'xyz', 'xyz'],
            'cusip': ['ABC', 'ABC', 'DEF', 'DEF', 'GHI', 'GHI', 'JKL', 'JKL'],
            'quantity': [2, 2, 2, 2, 2, 2, 2, 2]}

        df1 = pd.DataFrame(dummy_data1, columns=['acc', 'cusip', 'quantity'])

        aggregator = Aggregator()
        result = aggregator.execute(config, None, df1)
        expected_result = df1.groupby(['acc', 'cusip']).agg('sum', 'quantity').reset_index()

        self.assertTrue(pd.DataFrame.equals(result, expected_result))

    def test_execute_function_with_single_row(self):
        config = {'type': 'aggregate', 'groupby': {'cols': ['acc', 'cusip']},
                  'agg': {'operation': 'sum', 'col': 'quantity'}}

        dummy_data1 = {
            'acc': ['abcd'],
            'cusip': ['ABC'],
            'quantity': [2]}

        df1 = pd.DataFrame(dummy_data1, columns=['acc', 'cusip', 'quantity'])

        aggregator = Aggregator()
        result = aggregator.execute(config, None, df1)
        expected_result = df1.groupby(['acc', 'cusip']).agg('sum', 'quantity').reset_index()

        self.assertTrue(pd.DataFrame.equals(result, expected_result))

    def test_execute_function_with_zero_rows(self):
        config = {'type': 'aggregate', 'groupby': {'cols': ['acc', 'cusip']},
                  'agg': {'operation': 'sum', 'col': 'quantity'}}

        dummy_data1 = {
            'acc': [],
            'cusip': [],
            'quantity': []}

        df1 = pd.DataFrame(dummy_data1, columns=['acc', 'cusip', 'quantity'])

        aggregator = Aggregator()
        result = aggregator.execute(config, None, df1)
        expected_result = df1.groupby(['acc', 'cusip']).agg('sum', 'quantity').reset_index()

        self.assertTrue(pd.DataFrame.equals(result, expected_result))
