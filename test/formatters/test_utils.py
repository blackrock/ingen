#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest

import pandas as pd

from ingen.formatters.utils import *


class TestUtils(unittest.TestCase):
    def test_addition_function_with_multiple_rows(self):
        sample_data = pd.DataFrame({
            'weight1': [28, 39, 50],
            'weight2': [10, 15, 22],
            'weight3': [12, 23, 27],
            'weight4': [56, 13, 22]
        })
        col_name = 'sum'
        columns = ['weight1', 'weight2', 'weight3', 'weight4'];
        expected_data = sample_data.copy()
        expected_data[col_name] = [106, 90, 121]
        formatted_data = addition(sample_data, col_name, columns)
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_addition_function_without_rows_returns_same_dataframe(self):
        sample_data = pd.DataFrame({
            'weight1': [28, 39, 50],
            'weight2': [10, 15, 22],
            'weight3': [12, 23, 27],
            'weight4': [56, 13, 22]
        })
        col_name = 'sum'
        expected_data = sample_data.copy()
        formatted_data = addition(sample_data, col_name, None)
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_subtraction_function_with_multiple_rows(self):
        sample_data = pd.DataFrame({
            'weight1': [28, 39, 50],
            'weight2': [10, 19, 20],
            'weight3': [6, 5, 10],
            'weight4': [2, 5, 10]
        })
        col_name = 'sub'
        columns = ['weight1', 'weight2', 'weight3', 'weight4'];
        expected_data = sample_data.copy()
        expected_data[col_name] = [10, 10, 10]
        formatted_data = subtract(sample_data, col_name, columns)
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_subtraction_function_without_rows_returns_same_dataframe(self):
        sample_data = pd.DataFrame({
            'weight1': [28, 39, 50],
            'weight2': [10, 19, 20],
            'weight3': [6, 5, 10],
            'weight4': [2, 5, 10]
        })
        col_name = 'sum'
        expected_data = sample_data.copy()
        formatted_data = subtract(sample_data, col_name, None)
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_divide_function_with_multiple_rows(self):
        sample_data = pd.DataFrame({
            'weight1': [128, 32, 64],
            'weight2': [2, 2, 2],
            'weight3': [2, 2, 2],
            'weight4': [2, 2, 2]
        })
        col_name = 'div'
        columns = ['weight1', 'weight2', 'weight3', 'weight4'];
        expected_data = sample_data.copy()
        expected_data[col_name] = [16.0, 4.0, 8.0]
        formatted_data = divide(sample_data, col_name, columns)
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_divide_function_without_rows_returns_same_dataframe(self):
        sample_data = pd.DataFrame({
            'weight1': [28, 39, 50],
            'weight2': [10, 19, 20],
            'weight3': [6, 5, 10],
            'weight4': [2, 5, 10]
        })
        col_name = 'div'
        expected_data = sample_data.copy()
        formatted_data = divide(sample_data, col_name, None)
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_multiply_function_with_multiple_rows(self):
        sample_data = pd.DataFrame({
            'weight1': [16, 4, 8],
            'weight2': [2, 2, 2],
            'weight3': [2, 2, 2],
            'weight4': [2, 2, 2]
        })
        col_name = 'mul'
        columns = ['weight1', 'weight2', 'weight3', 'weight4'];
        expected_data = sample_data.copy()
        expected_data[col_name] = [128, 32, 64]
        formatted_data = multiply(sample_data, col_name, columns)
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_multiply_function_without_rows_returns_same_dataframe(self):
        sample_data = pd.DataFrame({
            'weight1': [28, 39, 50],
            'weight2': [10, 19, 20],
            'weight3': [6, 5, 10],
            'weight4': [2, 5, 10]
        })
        col_name = 'mul'
        expected_data = sample_data.copy()
        formatted_data = multiply(sample_data, col_name, None)
        pd.testing.assert_frame_equal(expected_data, formatted_data)
