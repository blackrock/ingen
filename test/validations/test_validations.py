import unittest

import pandas as pd

from ingen.validation.validations import Validation


class TestValidations(unittest.TestCase):

    def test_apply_validations_when_expect_column_values_to_not_be_null_with_no_null_values(self):
        columns = [
            {
                'src_col_name': 'ACCOUNT_ID',
                'validations': [
                    {
                        'type': 'expect_column_values_to_not_be_null',
                        'severity': 'warning'
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', 'Z88262440'],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        dataframe_expected = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', 'Z88262440'],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        validations = Validation(dataframe, columns)
        dataframe_actual, validation_summary = validations.apply_validations()
        pd.testing.assert_frame_equal(dataframe_actual, dataframe_expected)

    def test_apply_validations_when_expect_column_values_to_not_be_null_with_null_values_severity_warning(self):
        columns = [
            {
                'src_col_name': 'ACCOUNT_ID',
                'validations': [
                    {
                        'type': 'expect_column_values_to_not_be_null',
                        'severity': 'warning'
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', None],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        dataframe_expected = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', None],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        validations = Validation(dataframe, columns)
        dataframe_actual, validation_summary = validations.apply_validations()
        pd.testing.assert_frame_equal(dataframe_actual, dataframe_expected)

    def test_apply_validations_when_expect_column_values_to_not_be_null_with_null_values_severity_not_given(self):
        columns = [
            {
                'src_col_name': 'ACCOUNT_ID',
                'validations': [
                    {
                        'type': 'expect_column_values_to_not_be_null'
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', None]
        })
        dataframe_expected = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', None]
        })
        validations = Validation(dataframe, columns)
        dataframe_actual, validation_summary = validations.apply_validations()
        pd.testing.assert_frame_equal(dataframe_actual, dataframe_expected)

    def test_apply_validations_when_expect_column_values_to_not_be_null_with_null_values_severity_critical(self):
        columns = [
            {
                'src_col_name': 'ACCOUNT_ID',
                'validations': [
                    {
                        'type': 'expect_column_values_to_not_be_null',
                        'severity': 'critical'
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', None],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        dataframe_expected = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430'],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201']
        })
        validations = Validation(dataframe, columns)
        dataframe_actual, validation_summary = validations.apply_validations()
        pd.testing.assert_frame_equal(dataframe_actual, dataframe_expected)

    def test_apply_validations_when_expect_column_values_to_not_be_null_with_null_values_severity_blocker(self):
        columns = [
            {
                'src_col_name': 'ACCOUNT_ID',
                'validations': [
                    {
                        'type': 'expect_column_values_to_not_be_null',
                        'severity': 'blocker'
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', None],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        validations = Validation(dataframe, columns)
        _, validation_summary = validations.apply_validations()
        expected_validation_msg = 'Validation failed for column ACCOUNT_ID for expectation type : expect_column_values_to_not_be_null'
        actual_validation_msg = validation_summary[1]
        self.assertEqual(expected_validation_msg, actual_validation_msg)

    def test_apply_validations_when_type_none(self):
        columns = [
            {
                'src_col_name': 'ACCOUNT_ID',
                'validations': [
                    {
                        'type': 'expect_not_present',
                        'severity': 'critical'
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', None],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        validations = Validation(dataframe, columns)
        column_name = 'ACCOUNT_ID'
        expectation_type = 'expect_not_present'
        with self.assertRaisesRegex(ValueError, f"Invalid validation type: {expectation_type} on column {column_name}"):
            validations.apply_validations()

    def test_apply_validations_when_expect_column_values_to_match_regex_list_with_severity_critical(self):
        columns = [
            {
                'src_col_name': 'ACCOUNT_ID',
                'validations': [
                    {
                        'type': 'expect_column_values_to_match_regex_list',
                        'severity': 'critical',
                        'args': [["^[a-zA-Z0-9]{9}$"]]
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', '10'],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        dataframe_expected = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430'],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201']
        })
        validations = Validation(dataframe, columns)
        dataframe_actual, validation_summary = validations.apply_validations()
        pd.testing.assert_frame_equal(dataframe_actual, dataframe_expected)

    def test_apply_validations_when_expect_column_values_to_match_regex_list_with_severity_blocker(self):
        columns = [
            {
                'src_col_name': 'ACCOUNT_ID',
                'validations': [
                    {
                        'type': 'expect_column_values_to_match_regex_list',
                        'severity': 'blocker',
                        'args': [["^[a-zA-Z0-9]{9}$"]]
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', '10'],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        validations = Validation(dataframe, columns)
        _, validation_summary = validations.apply_validations()
        expected_validation_msg = 'Validation failed for column ACCOUNT_ID for expectation type : expect_column_values_to_match_regex_list'
        actual_validation_msg = validation_summary[1]
        self.assertEqual(expected_validation_msg, actual_validation_msg)

    def test_expect_column_values_to_match_strftime_format_with_severity_critical(self):
        columns = [
            {
                'src_col_name': 'DATE',
                'validations': [
                    {
                        'type': 'expect_column_values_to_match_regex_list',
                        'severity': 'critical',
                        'args': ['%Y-%m-%d']
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', 'Z88262430'],
            'DATE': ['2020-01-10', '2010-04-26', '2008-11-13', '2022-08-26', '2022/07/07']
        })
        dataframe_expected = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430'],
            'DATE': ['2020-01-10', '2010-04-26', '2008-11-13', '2022-08-26']
        })
        validations = Validation(dataframe, columns)
        dataframe_actual, validation_summary = validations.apply_validations()
        pd.testing.assert_frame_equal(dataframe_actual, dataframe_expected)

    def test_expect_column_values_to_match_strftime_format_with_severity_blocker(self):
        columns = [
            {
                'src_col_name': 'DATE',
                'validations': [
                    {
                        'type': 'expect_column_values_to_match_regex_list',
                        'severity': 'blocker',
                        'args': ['%Y-%m-%d']
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', 'Z88262430'],
            'DATE': ['2020-01-10', '2010-04-26', '2008-11-13', '2022-08-26', '2022/07/07']
        })
        validations = Validation(dataframe, columns)
        _, validation_summary = validations.apply_validations()
        expected_validation_msg = 'Validation failed for column DATE for expectation type : expect_column_values_to_match_regex_list'
        actual_validation_msg = validation_summary[1]
        self.assertEqual(expected_validation_msg, actual_validation_msg)

    def test_expect_column_values_to_be_between_with_severity_critical(self):
        columns = [
            {
                'src_col_name': 'WEIGHT',
                'validations': [
                    {
                        'type': 'expect_column_values_to_be_between',
                        'severity': 'critical',
                        'args': [0, 10]
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'WEIGHT': [0, 3, 5, 7, 13]
        })
        dataframe_expected = pd.DataFrame({
            'WEIGHT': [0, 3, 5, 7]
        })
        validations = Validation(dataframe, columns)
        dataframe_actual, validation_summary = validations.apply_validations()
        pd.testing.assert_frame_equal(dataframe_actual, dataframe_expected)

    def test_expect_column_values_to_be_between_with_severity_blocker(self):
        columns = [
            {
                'src_col_name': 'WEIGHT',
                'validations': [
                    {
                        'type': 'expect_column_values_to_be_between',
                        'severity': 'blocker',
                        'args': [0, 10]
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'WEIGHT': [0, 3, 5, 7, 13]
        })
        validations = Validation(dataframe, columns)
        _, validation_summary = validations.apply_validations()
        expected_validation_msg = 'Validation failed for column WEIGHT for expectation type : expect_column_values_to_be_between'
        actual_validation_msg = validation_summary[1]
        self.assertEqual(expected_validation_msg, actual_validation_msg)

    def test_expect_column_values_to_be_unique_with_severity_critical(self):
        columns = [
            {
                'src_col_name': 'WEIGHT',
                'validations': [
                    {
                        'type': 'expect_column_values_to_be_unique',
                        'severity': 'critical'
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'WEIGHT': [0, 3, 5, 7, 7]
        })
        dataframe_expected = pd.DataFrame({
            'WEIGHT': [0, 3, 5]
        })
        validations = Validation(dataframe, columns)
        dataframe_actual, validation_summary = validations.apply_validations()
        pd.testing.assert_frame_equal(dataframe_actual, dataframe_expected)

    def test_expect_column_values_to_be_unique_with_severity_blocker(self):
        columns = [
            {
                'src_col_name': 'WEIGHT',
                'validations': [
                    {
                        'type': 'expect_column_values_to_be_unique',
                        'severity': 'blocker'
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'WEIGHT': [0, 3, 5, 7, 7]
        })
        validations = Validation(dataframe, columns)
        _, validation_summary = validations.apply_validations()
        expected_validation_msg = 'Validation failed for column WEIGHT for expectation type : expect_column_values_to_be_unique'
        actual_validation_msg = validation_summary[1]
        self.assertEqual(expected_validation_msg, actual_validation_msg)

    def test_expect_column_value_lengths_to_equal_with_severity_critical(self):
        columns = [
            {
                'src_col_name': 'ACCOUNT_ID',
                'validations': [
                    {
                        'type': 'expect_column_value_lengths_to_equal',
                        'severity': 'critical',
                        'args': [9]
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z0', 'Z88262430']
        })
        validations = Validation(dataframe, columns)
        _, validation_summary = validations.apply_validations()
        expected_validation_msg = 'Validation failed for column ACCOUNT_ID for expectation type : expect_column_value_lengths_to_equal'
        actual_validation_msg = validation_summary[1]
        self.assertEqual(expected_validation_msg, actual_validation_msg)

    def test_expect_column_value_lengths_to_equal_with_severity_blocker(self):
        columns = [
            {
                'src_col_name': 'ACCOUNT_ID',
                'validations': [
                    {
                        'type': 'expect_column_value_lengths_to_equal',
                        'severity': 'blocker',
                        'args': [9]
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', 'Z0']
        })
        validations = Validation(dataframe, columns)
        _, validation_summary = validations.apply_validations()
        expected_validation_msg = 'Validation failed for column ACCOUNT_ID for expectation type : expect_column_value_lengths_to_equal'
        actual_validation_msg = validation_summary[1]
        self.assertEqual(expected_validation_msg, actual_validation_msg)

    def test_expect_column_values_to_be_of_type_with_type_float_severity_as_critical(self):
        columns = [
            {
                'src_col_name': 'WEIGHT',
                'validations': [
                    {
                        'type': 'expect_column_values_to_be_of_type',
                        'severity': 'critical',
                        'args': ['float']
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'WEIGHT': ['0', '1', '2Inv', '0.3', '3.4']
        })
        validations = Validation(dataframe, columns)
        _, validation_summary = validations.apply_validations()
        expected_validation_msg = 'Validation failed for column WEIGHT for expectation type : expect_column_values_to_be_of_type'
        actual_validation_msg = validation_summary[1]
        self.assertEqual(expected_validation_msg, actual_validation_msg)

    def test_expect_column_values_to_be_of_type_with_type_int_severity_as_critical(self):
        columns = [
            {
                'src_col_name': 'WEIGHT',
                'validations': [
                    {
                        'type': 'expect_column_values_to_be_of_type',
                        'severity': 'critical',
                        'args': ['int']
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'WEIGHT': ['0', '1', '2Inv', '0.3', '3.4']
        })
        dataframe_expected = pd.DataFrame({
            'WEIGHT': ['0', '1']
        })
        validations = Validation(dataframe, columns)
        dataframe_actual, validation_summary = validations.apply_validations()
        pd.testing.assert_series_equal(dataframe_actual['WEIGHT'], dataframe_expected['WEIGHT'])

    def test_expect_column_values_to_be_of_type_with_type_str_severity_as_critical(self):
        columns = [
            {
                'src_col_name': 'WEIGHT',
                'validations': [
                    {
                        'type': 'expect_column_values_to_be_of_type',
                        'severity': 'critical',
                        'args': ['str']
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'WEIGHT': ['0', 1, 3, 4]
        })
        dataframe_expected = pd.DataFrame({
            'WEIGHT': ['0', 1, 3, 4]
        })
        validations = Validation(dataframe, columns)
        dataframe_actual, validation_summary = validations.apply_validations()
        pd.testing.assert_series_equal(dataframe_actual['WEIGHT'], dataframe_expected['WEIGHT'])

    def test_expect_column_to_contain_values(self):
        columns = [
            {
                'src_col_name': 'WEIGHT',
                'validations': [
                    {
                        'type': 'expect_column_to_contain_values',
                        'severity': 'blocker',
                        'args': [['2Inv', 'value']]
                    }
                ]
            }
        ]
        dataframe = pd.DataFrame({
            'WEIGHT': ['0', '1', '2Inv', '0.3', '3.4']
        })
        validations = Validation(dataframe, columns)
        _, validation_summary = validations.apply_validations()
        expected_validation_msg = 'Validation failed for column WEIGHT for expectation type : expect_column_to_contain_values'
        actual_validation_msg = validation_summary[1]
        self.assertEqual(expected_validation_msg, actual_validation_msg)

    def test_expect_column_values_to_be_present_in(self):
        columns = [
            {
                'src_col_name': 'CUSIP',
                'validations': [
                    {
                        'type': 'expect_column_values_to_be_present_in',
                        'severity': 'critical',
                        'args': [['source1', 'ID']]
                    }
                ]
            }
        ]
        data = {
            'source1': pd.DataFrame({
                'CUSIP': ['0', '1', '0.3', '3.4'],
                'ID': ['0', '1', '0.3', '3.4']
            })
        }
        dataframe = pd.DataFrame({
            'CUSIP': ['0', '1', '2Inv', '0.3', '3.4'],
            'ID': ['0', '1', '3', '0.3', '3.4']
        })
        validations = Validation(dataframe, columns, data=data)
        _, validation_summary = validations.apply_validations()
        expected_validation_msg = 'Validation failed for column CUSIP for expectation type : expect_column_values_to_be_present_in'
        actual_validation_msg = validation_summary[1]
        self.assertEqual(expected_validation_msg, actual_validation_msg)

    def test_expect_column_values_to_be_present_in_when_given_source_wrong(self):
        columns = [
            {
                'src_col_name': 'CUSIP',
                'validations': [
                    {
                        'type': 'expect_column_values_to_be_present_in',
                        'severity': 'critical',
                        'args': [['wrong_source', 'ID']]
                    }
                ]
            }
        ]
        data = {
            'source1': pd.DataFrame({
                'CUSIP': ['0', '1', '0.3', '3.4'],
                'ID': ['0', '1', '0.3', '3.4']
            })
        }
        dataframe = pd.DataFrame({
            'CUSIP': ['0', '1', '2Inv', '0.3', '3.4'],
            'ID': ['0', '1', '3', '0.3', '3.4']
        })
        validation = Validation(dataframe, columns, data=data)
        with self.assertRaisesRegex(ValueError, "Invalid wrong_source or ID unable to find in source"):
            validation.apply_validations()
