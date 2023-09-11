#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest

import great_expectations as ge
import pandas as pd

from ingen.validation.common_validations import *


class TestCommonValidations(unittest.TestCase):

    def test_validate_when_severity_warning(self):
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', None],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        ge_dataframe = ge.from_pandas(dataframe)
        column_name = 'ACCOUNT_ID'
        validation_options = {
            'severity': 'warning'
        }

        validation_type = 'expect_column_values_to_not_be_null'
        validation_func = getattr(ge_dataframe, validation_type)
        validation_func(column_name, meta=validation_options)
        dataframe_actual, validation_summary = validate(dataframe, ge_dataframe)

        dataframe_expected = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', None],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        pd.testing.assert_frame_equal(dataframe_expected, dataframe_actual)

    def test_validate_when_severity_critical(self):
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', None],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        ge_dataframe = ge.from_pandas(dataframe)
        column_name = 'ACCOUNT_ID'
        validation_options = {
            'severity': 'critical'
        }

        validation_type = 'expect_column_values_to_not_be_null'
        validation_func = getattr(ge_dataframe, validation_type)
        validation_func(column_name, meta=validation_options)
        dataframe_actual, validation_summary = validate(dataframe, ge_dataframe)

        dataframe_expected = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430'],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201']
        })
        pd.testing.assert_frame_equal(dataframe_expected, dataframe_actual)

    def test_validate_when_severity_blocker(self):
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', None],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        ge_dataframe = ge.from_pandas(dataframe)
        column_name = 'ACCOUNT_ID'
        validation_options = {
            'severity': 'blocker'
        }

        validation_type = 'expect_column_values_to_not_be_null'
        validation_func = getattr(ge_dataframe, validation_type)
        validation_func(column_name, meta=validation_options)
        _, validation_summary = validate(dataframe, ge_dataframe)
        actual_validation_severity = validation_summary[0]
        self.assertEqual(actual_validation_severity, 'severity : blocker')

    def test_expect_column_values_to_not_be_null(self):
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', 'Z88262440']
        })
        ge_dataframe_arg = ge.from_pandas(dataframe)
        column_name = 'ACCOUNT_ID'
        validation_options = {
            'severity': 'critical'
        }

        ge_dataframe_expected = ge.from_pandas(dataframe)
        ge_dataframe_expected.expect_column_values_to_not_be_null(column_name,
                                                                  meta={'severity': validation_options['severity']})
        validation_type = 'expect_column_values_to_not_be_null'
        validation_func = getattr(ge_dataframe_arg, validation_type)
        validation_func(column_name)

        expected_validate_dict = ge_dataframe_expected.validate()
        actual_validate_dict = ge_dataframe_arg.validate()

        self.assertEqual(expected_validate_dict.get('results'), actual_validate_dict.get('results'))
        self.assertEqual(expected_validate_dict.get('statistics'), actual_validate_dict.get('statistics'))

    def test_expect_column_values_to_match_regex_list(self):
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', 'Z88'],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        ge_dataframe_arg = ge.from_pandas(dataframe)
        column_name = 'ACCOUNT_ID'
        validation_options = {
            'regex_list': ["^[a-zA-Z0-9]{9}$"],
            'severity': 'critical'
        }

        ge_dataframe_expected = ge.from_pandas(dataframe)
        ge_dataframe_expected.expect_column_values_to_match_regex_list(column_name, validation_options['regex_list'],
                                                                       meta={
                                                                           'severity': validation_options['severity']})
        validation_type = 'expect_column_values_to_match_regex_list'
        validation_func = getattr(ge_dataframe_arg, validation_type)
        validation_func(column_name, validation_options['regex_list'])

        expected_validate_dict = ge_dataframe_expected.validate()
        actual_validate_dict = ge_dataframe_arg.validate()

        self.assertEqual(expected_validate_dict.get('results'), actual_validate_dict.get('results'))
        self.assertEqual(expected_validate_dict.get('statistics'), actual_validate_dict.get('statistics'))

    def test_expect_column_values_to_match_strftime_format(self):
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', 'Z88262430'],
            'DATE': ['2020-01-10', '2010-04-26', '2008-11-13', '2022-08-26', '2022-07-07']
        })
        ge_dataframe_arg = ge.from_pandas(dataframe)
        column_name = 'DATE'
        validation_options = {
            'format_option': '%Y-%m-%d',
            'severity': 'critical'
        }

        ge_dataframe_expected = ge.from_pandas(dataframe)
        ge_dataframe_expected.expect_column_values_to_match_strftime_format(column_name,
                                                                            validation_options['format_option'],
                                                                            meta={'severity': validation_options[
                                                                                'severity']})
        validation_type = 'expect_column_values_to_match_strftime_format'
        validation_func = getattr(ge_dataframe_arg, validation_type)
        validation_func(column_name, validation_options['format_option'])

        expected_validate_dict = ge_dataframe_expected.validate()
        actual_validate_dict = ge_dataframe_arg.validate()

        self.assertEqual(expected_validate_dict.get('results'), actual_validate_dict.get('results'))
        self.assertEqual(expected_validate_dict.get('statistics'), actual_validate_dict.get('statistics'))

    def test_expect_column_values_to_be_between(self):
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', 'Z88262430'],
            'WEIGHT': [0, 1, 2, 3, 4]
        })
        ge_dataframe_arg = ge.from_pandas(dataframe)
        column_name = 'WEIGHT'
        min_value = 0
        max_value = 10
        validation_options = {
            'type': 'expect_column_values_to_be_between',
            'severity': 'critical',
            'min_value': min_value,
            'max_value': max_value
        }

        ge_dataframe_expected = ge.from_pandas(dataframe)
        ge_dataframe_expected.expect_column_values_to_be_between(column_name, min_value, max_value,
                                                                 meta={'severity': validation_options['severity']})
        validation_type = validation_options['type']
        validation_func = getattr(ge_dataframe_arg, validation_type)
        validation_func(column_name, validation_options['min_value'], validation_options['max_value'])

        expected_validate_dict = ge_dataframe_expected.validate()
        actual_validate_dict = ge_dataframe_arg.validate()

        self.assertEqual(expected_validate_dict.get('results'), actual_validate_dict.get('results'))
        self.assertEqual(expected_validate_dict.get('statistics'), actual_validate_dict.get('statistics'))

    def test_expect_column_values_to_be_unique(self):
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', 'Z88262430'],
            'WEIGHT': [0, 1, 2, 3, 4]
        })
        ge_dataframe_arg = ge.from_pandas(dataframe)
        column_name = 'WEIGHT'
        validation_options = {
            'type': 'expect_column_values_to_be_unique',
            'severity': 'critical',
        }

        ge_dataframe_expected = ge.from_pandas(dataframe)
        ge_dataframe_expected.expect_column_values_to_be_unique(column_name,
                                                                meta={'severity': validation_options['severity']})
        validation_type = validation_options['type']
        validation_func = getattr(ge_dataframe_arg, validation_type)
        validation_func(column_name)

        expected_validate_dict = ge_dataframe_expected.validate()
        actual_validate_dict = ge_dataframe_arg.validate()

        self.assertEqual(expected_validate_dict.get('results'), actual_validate_dict.get('results'))
        self.assertEqual(expected_validate_dict.get('statistics'), actual_validate_dict.get('statistics'))

    def test_expect_column_value_lengths_to_equal(self):
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', 'Z88262430'],
            'WEIGHT': [0, 1, 2, 3, 4]
        })
        ge_dataframe_arg = ge.from_pandas(dataframe)
        column_name = 'ACCOUNT_ID'
        value_length = 9
        validation_options = {
            'type': 'expect_column_value_lengths_to_equal',
            'severity': 'critical',
            'value_length': value_length
        }

        ge_dataframe_expected = ge.from_pandas(dataframe)
        ge_dataframe_expected.expect_column_value_lengths_to_equal(column_name, value_length,
                                                                   meta={'severity': validation_options['severity']})
        validation_type = validation_options['type']
        validation_func = getattr(ge_dataframe_arg, validation_type)
        validation_func(column_name, validation_options['value_length'])

        expected_validate_dict = ge_dataframe_expected.validate()
        actual_validate_dict = ge_dataframe_arg.validate()

        self.assertEqual(expected_validate_dict.get('results'), actual_validate_dict.get('results'))
        self.assertEqual(expected_validate_dict.get('statistics'), actual_validate_dict.get('statistics'))
