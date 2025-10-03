#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pytest

import numpy as np
import pandas as pd

from ingen.pre_processor.union import Union


class TestDFUnion:

    def test_union_with_multiple_df(self):
        dummy_data1 = {
            'id': ['1', '2', '6', '7', '8'],
            'Feature1': ['K', 'M', 'O', 'Q', 'S'],
            'Feature2': ['L', 'N', 'P', 'R', 'T']}

        df1 = pd.DataFrame(dummy_data1, columns=['id', 'Feature1', 'Feature2'])

        dummy_data2 = {
            'id': ['9', '10'],
            'Feature1': ['U', 'V'],
            'Feature2': ['W', 'X']}

        df2 = pd.DataFrame(dummy_data2, columns=['id', 'Feature1', 'Feature2'])

        dummy_data3 = {
            'id': ['11', '12'],
            'Feature1': ['Y', 'Z'],
            'Feature2': ['A', 'B']}

        df3 = pd.DataFrame(dummy_data3, columns=['id', 'Feature1', 'Feature2'])

        expected_result = {
            'id': ['1', '2', '6', '7', '8', '9', '10', '11', '12'],
            'Feature1': ['K', 'M', 'O', 'Q', 'S', 'U', 'V', 'Y', 'Z'],
            'Feature2': ['L', 'N', 'P', 'R', 'T', 'W', 'X', 'A', 'B']}
        expected_df = pd.DataFrame(expected_result, columns=['id', 'Feature1', 'Feature2'])

        config = {'type': 'union', 'source': ['source1', 'source2', 'source3']}
        obj = Union()
        result = obj.execute(config, {'source1': df1, 'source2': df2, 'source3': df3}, None)
        pd.testing.assert_frame_equal(expected_df.reset_index(drop=True), result.reset_index(drop=True))

    def test_union_with_multiple_df_diff_cols(self):
        dummy_data1 = {
            'id': ['1', '2', '6', '7', '8'],
            'Feature1': ['K', 'M', 'O', 'Q', 'S'],
            'Feature2': ['L', 'N', 'P', 'R', 'T']}

        df1 = pd.DataFrame(dummy_data1, columns=['id', 'Feature1', 'Feature2'])

        dummy_data2 = {
            'id': ['9', '10'],
            'Feature1': ['U', 'V'],
            'Feature2': ['W', 'X'],
            'Feature3': ['HELLO', 'WORLD']}

        df2 = pd.DataFrame(dummy_data2, columns=['id', 'Feature1', 'Feature2', 'Feature3'])

        expected_result = {
            'id': ['1', '2', '6', '7', '8', '9', '10'],
            'Feature1': ['K', 'M', 'O', 'Q', 'S', 'U', 'V'],
            'Feature2': ['L', 'N', 'P', 'R', 'T', 'W', 'X'],
            'Feature3': [np.nan, np.nan, np.nan, np.nan, np.nan, 'HELLO', 'WORLD']}
        expected_df = pd.DataFrame(expected_result, columns=['id', 'Feature1', 'Feature2', 'Feature3'])

        config = {'type': 'union', 'source': ['source1', 'source2']}
        obj = Union()
        result = obj.execute(config, {'source1': df1, 'source2': df2}, None)

        pd.testing.assert_frame_equal(expected_df.reset_index(drop=True), result.reset_index(drop=True))

    def test_union_with_columns(self):
        dummy_data1 = {
            'id': ['1', '2', '3', '4', '5'],
            'Feature1': ['K', 'M', 'O', 'Q', 'S'],
            'Feature2': ['L', 'N', 'P', 'R', 'T']}

        df1 = pd.DataFrame(dummy_data1, columns=['id', 'Feature1', 'Feature2'])

        dummy_data2 = {
            'Feature3': ['A', 'B', 'C', 'D', 'E']}

        df2 = pd.DataFrame(dummy_data2, columns=['Feature3'])

        expected_result = {
            'id': ['1', '2', '3', '4', '5'],
            'Feature1': ['K', 'M', 'O', 'Q', 'S'],
            'Feature2': ['L', 'N', 'P', 'R', 'T'],
            'Feature3': ['A', 'B', 'C', 'D', 'E']}
        expected_df = pd.DataFrame(expected_result, columns=['id', 'Feature1', 'Feature2', 'Feature3'])

        config = {'type': 'union', 'source': ['source1', 'source2'], 'direction': 1}
        obj = Union()
        result = obj.execute(config, {'source1': df1, 'source2': df2}, None)
        pd.testing.assert_frame_equal(expected_df, result)

    def test_union_with_columns_with_unequal_rows(self):
        dummy_data1 = {
            'id': ['1', '2', '3', '4', '5'],
            'Feature1': ['K', 'M', 'O', 'Q', 'S'],
            'Feature2': ['L', 'N', 'P', 'R', 'T']}

        df1 = pd.DataFrame(dummy_data1, columns=['id', 'Feature1', 'Feature2'])

        dummy_data2 = {
            'Feature3': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']}

        df2 = pd.DataFrame(dummy_data2, columns=['Feature3'])

        expected_result = {
            'id': ['1', '2', '3', '4', '5', np.nan, np.nan, np.nan],
            'Feature1': ['K', 'M', 'O', 'Q', 'S', np.nan, np.nan, np.nan],
            'Feature2': ['L', 'N', 'P', 'R', 'T', np.nan, np.nan, np.nan],
            'Feature3': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']}
        expected_df = pd.DataFrame(expected_result, columns=['id', 'Feature1', 'Feature2', 'Feature3'])

        config = {'type': 'union', 'source': ['source1', 'source2'], 'direction': 1}
        obj = Union()
        result = obj.execute(config, {'source1': df1, 'source2': df2}, None)
        pd.testing.assert_frame_equal(expected_df, result)

    def test_union_with_invalid_axis_value(self):
        dummy_data1 = {
            'id': ['1', '2', '3', '4', '5'],
            'Feature1': ['K', 'M', 'O', 'Q', 'S'],
            'Feature2': ['L', 'N', 'P', 'R', 'T']}

        df1 = pd.DataFrame(dummy_data1, columns=['id', 'Feature1', 'Feature2'])

        dummy_data2 = {
            'Feature3': ['A', 'B', 'C', 'D', 'E']}

        df2 = pd.DataFrame(dummy_data2, columns=['Feature3'])

        config = {'type': 'union', 'source': ['source1', 'source2'], 'direction': 'c'}
        obj = Union()
        with pytest.raises(KeyError):
            obj.execute(config, {'source1': df1, 'source2': df2}, None)
