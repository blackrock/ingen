#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest

import pandas as pd

from ingen.pre_processor.json_array_expander import JsonArrayExpander


class TestJsonArrayExpander(unittest.TestCase):

    def setUp(self):
        self.expander = JsonArrayExpander()

    def test_basic_expansion(self):
        """Test basic JSON array expansion"""
        config = {
            "config": {
                "column": "holdings"
            }
        }

        data = pd.DataFrame({
            "identifier": ["PORTFOLIO1"],
            "holdings": [
                '[{"cusip": "12345", "holdingPercent": 0.15, "globalId": "G1"}, {"cusip": "67890", "holdingPercent": 0.25, "globalId": "G2"}]']
        })

        result = self.expander.execute(config, {}, data)

        expected = pd.DataFrame({
            "identifier": ["PORTFOLIO1", "PORTFOLIO1"],
            "cusip": ["12345", "67890"],
            "holdingPercent": [0.15, 0.25],
            "globalId": ["G1", "G2"]
        })

        pd.testing.assert_frame_equal(result.sort_index(axis=1), expected.sort_index(axis=1))

    def test_include_columns_filter(self):
        """Test expansion with include_columns filter"""
        config = {
            "config": {
                "column": "holdings",
                "include_columns": ["cusip", "holdingPercent"]
            }
        }

        data = pd.DataFrame({
            "identifier": ["PORTFOLIO1"],
            "holdings": ['[{"cusip": "12345", "holdingPercent": 0.15, "globalId": "G1", "asOfDate": "2023-01-01"}]']
        })

        result = self.expander.execute(config, {}, data)

        expected = pd.DataFrame({
            "identifier": ["PORTFOLIO1"],
            "cusip": ["12345"],
            "holdingPercent": [0.15]
        })

        pd.testing.assert_frame_equal(result.sort_index(axis=1), expected.sort_index(axis=1))

    def test_exclude_columns_filter(self):
        """Test expansion with exclude_columns filter"""
        config = {
            "config": {
                "column": "holdings",
                "exclude_columns": ["globalId"]
            }
        }

        data = pd.DataFrame({
            "identifier": ["PORTFOLIO1"],
            "holdings": ['[{"cusip": "12345", "holdingPercent": 0.15, "globalId": "G1"}]']
        })

        result = self.expander.execute(config, {}, data)

        expected = pd.DataFrame({
            "identifier": ["PORTFOLIO1"],
            "cusip": ["12345"],
            "holdingPercent": [0.15]
        })

        pd.testing.assert_frame_equal(result.sort_index(axis=1), expected.sort_index(axis=1))

    def test_empty_json_string(self):
        """Test handling of empty JSON strings"""
        config = {
            "config": {
                "column": "holdings",
                "include_columns": ["cusip", "holdingPercent"]
            }
        }

        data = pd.DataFrame({
            "identifier": ["PORTFOLIO1", "PORTFOLIO2"],
            "holdings": ['[{"cusip": "12345", "holdingPercent": 0.15}]', '']
        })

        result = self.expander.execute(config, {}, data)

        expected = pd.DataFrame({
            "identifier": ["PORTFOLIO1", "PORTFOLIO2"],
            "cusip": ["12345", None],
            "holdingPercent": [0.15, None]
        })

        pd.testing.assert_frame_equal(result.sort_index(axis=1), expected.sort_index(axis=1))

    def test_null_json_string(self):
        """Test handling of null JSON strings"""
        config = {
            "config": {
                "column": "holdings",
                "include_columns": ["cusip", "holdingPercent"]
            }
        }

        data = pd.DataFrame({
            "identifier": ["PORTFOLIO1", "PORTFOLIO2"],
            "holdings": ['[{"cusip": "12345", "holdingPercent": 0.15}]', None]
        })

        result = self.expander.execute(config, {}, data)

        expected = pd.DataFrame({
            "identifier": ["PORTFOLIO1", "PORTFOLIO2"],
            "cusip": ["12345", None],
            "holdingPercent": [0.15, None]
        })

        pd.testing.assert_frame_equal(result.sort_index(axis=1), expected.sort_index(axis=1))

    def test_malformed_json(self):
        """Test handling of malformed JSON strings"""
        config = {
            "config": {
                "column": "holdings",
                "include_columns": ["cusip", "holdingPercent"]
            }
        }

        data = pd.DataFrame({
            "identifier": ["PORTFOLIO1", "PORTFOLIO2"],
            "holdings": ['[{"cusip": "12345", "holdingPercent": 0.15}]', '{"invalid": json}']
        })

        result = self.expander.execute(config, {}, data)

        expected = pd.DataFrame({
            "identifier": ["PORTFOLIO1", "PORTFOLIO2"],
            "cusip": ["12345", None],
            "holdingPercent": [0.15, None]
        })

        pd.testing.assert_frame_equal(result.sort_index(axis=1), expected.sort_index(axis=1))

    def test_multiple_portfolios(self):
        """Test expansion with multiple portfolios"""
        config = {
            "config": {
                "column": "holdings",
                "include_columns": ["cusip", "holdingPercent"]
            }
        }

        data = pd.DataFrame({
            "identifier": ["PORTFOLIO1", "PORTFOLIO2"],
            "holdings": [
                '[{"cusip": "12345", "holdingPercent": 0.15}, {"cusip": "67890", "holdingPercent": 0.25}]',
                '[{"cusip": "11111", "holdingPercent": 0.30}]'
            ]
        })

        result = self.expander.execute(config, {}, data)

        expected = pd.DataFrame({
            "identifier": ["PORTFOLIO1", "PORTFOLIO1", "PORTFOLIO2"],
            "cusip": ["12345", "67890", "11111"],
            "holdingPercent": [0.15, 0.25, 0.30]
        })

        pd.testing.assert_frame_equal(result.sort_index(axis=1), expected.sort_index(axis=1))

    def test_preserve_additional_columns(self):
        """Test that additional columns are preserved during expansion"""
        config = {
            "config": {
                "column": "holdings",
                "include_columns": ["cusip", "holdingPercent"]
            }
        }

        data = pd.DataFrame({
            "identifier": ["PORTFOLIO1"],
            "model_id": ["MODEL_A"],
            "as_of_date": ["2023-01-01"],
            "holdings": ['[{"cusip": "12345", "holdingPercent": 0.15}, {"cusip": "67890", "holdingPercent": 0.25}]']
        })

        result = self.expander.execute(config, {}, data)

        expected = pd.DataFrame({
            "identifier": ["PORTFOLIO1", "PORTFOLIO1"],
            "model_id": ["MODEL_A", "MODEL_A"],
            "as_of_date": ["2023-01-01", "2023-01-01"],
            "cusip": ["12345", "67890"],
            "holdingPercent": [0.15, 0.25]
        })

        pd.testing.assert_frame_equal(result.sort_index(axis=1), expected.sort_index(axis=1))

    def test_empty_dataframe(self):
        """Test handling of empty dataframe."""
        df = pd.DataFrame(columns=['portfolio', 'holdings'])
        config = {'column': 'holdings'}

        result = self.expander.execute(config, {}, df)

        pd.testing.assert_frame_equal(result, df)

    def test_non_list_json_values(self):
        """Test handling of JSON values that are not arrays."""
        df = pd.DataFrame({
            'portfolio': ['A', 'B', 'C'],
            'holdings': ['{"key": "value"}', '"string_value"', '123']
        })
        config = {'column': 'holdings'}

        result = self.expander.execute(config, {}, df)

        # Should create empty rows for non-array JSON
        expected = pd.DataFrame({
            'portfolio': ['A', 'B', 'C']
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_empty_json_arrays(self):
        """Test handling of empty JSON arrays."""
        df = pd.DataFrame({
            'portfolio': ['A', 'B'],
            'holdings': ['[]', '[{"ticker": "AAPL"}]']
        })
        config = {'column': 'holdings'}

        result = self.expander.execute(config, {}, df)

        expected = pd.DataFrame({
            'portfolio': ['A', 'B'],
            'ticker': [None, 'AAPL']
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_mixed_object_types_in_array(self):
        """Test handling of arrays with mixed object types (dicts and non-dicts)."""
        df = pd.DataFrame({
            'portfolio': ['A'],
            'holdings': ['[{"ticker": "AAPL"}, "invalid_object", {"ticker": "GOOGL"}]']
        })
        config = {'column': 'holdings'}

        result = self.expander.execute(config, {}, df)

        expected = pd.DataFrame({
            'portfolio': ['A', 'A', 'A'],
            'ticker': ['AAPL', None, 'GOOGL']
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_nested_json_values(self):
        """Test handling of nested objects and arrays in JSON values."""
        df = pd.DataFrame({
            'portfolio': ['A'],
            'holdings': ['[{"ticker": "AAPL", "details": {"sector": "Tech"}, "allocations": [10, 20]}]']
        })
        config = {'column': 'holdings'}

        result = self.expander.execute(config, {}, df)

        expected = pd.DataFrame({
            'portfolio': ['A'],
            'ticker': ['AAPL'],
            'details': ['{"sector": "Tech"}'],
            'allocations': ['[10, 20]']
        })
        pd.testing.assert_frame_equal(result.sort_index(axis=1), expected.sort_index(axis=1))

    def test_conflicting_filters(self):
        """Test warning when both include and exclude filters are specified."""
        df = pd.DataFrame({
            'portfolio': ['A'],
            'holdings': ['[{"ticker": "AAPL", "weight": 0.5, "sector": "Tech"}]']
        })
        config = {
            'column': 'holdings',
            'include_columns': ['ticker', 'weight'],
            'exclude_columns': ['sector']
        }

        with self.assertLogs(level='WARNING') as log_context:
            result = self.expander.execute(config, {}, df)

        # Should use include_columns and ignore exclude_columns
        expected = pd.DataFrame({
            'portfolio': ['A'],
            'ticker': ['AAPL'],
            'weight': [0.5]
        })
        pd.testing.assert_frame_equal(result.sort_index(axis=1), expected.sort_index(axis=1))

        # Check warning was logged
        self.assertTrue(any('Both include_columns and exclude_columns specified' in record.message
                            for record in log_context.records))

    def test_no_matching_include_columns(self):
        """Test warning when include_columns don't match any JSON keys."""
        df = pd.DataFrame({
            'portfolio': ['A'],
            'holdings': ['[{"ticker": "AAPL", "weight": 0.5}]']
        })
        config = {
            'column': 'holdings',
            'include_columns': ['nonexistent_key']
        }

        with self.assertLogs(level='WARNING') as log_context:
            result = self.expander.execute(config, {}, df)

        expected = pd.DataFrame({
            'portfolio': ['A']
        })
        pd.testing.assert_frame_equal(result, expected)

        # Check warning was logged
        self.assertTrue(any('No keys found matching include_columns' in record.message
                            for record in log_context.records))

    def test_all_keys_excluded(self):
        """Test warning when exclude_columns excludes all available keys."""
        df = pd.DataFrame({
            'portfolio': ['A'],
            'holdings': ['[{"ticker": "AAPL", "weight": 0.5}]']
        })
        config = {
            'column': 'holdings',
            'exclude_columns': ['ticker', 'weight']
        }

        with self.assertLogs(level='WARNING') as log_context:
            result = self.expander.execute(config, {}, df)

        expected = pd.DataFrame({
            'portfolio': ['A']
        })
        pd.testing.assert_frame_equal(result, expected)

        # Check warning was logged
        self.assertTrue(any('All keys excluded by exclude_columns' in record.message
                            for record in log_context.records))

    def test_whitespace_only_json_strings(self):
        """Test handling of whitespace-only JSON strings."""
        df = pd.DataFrame({
            'portfolio': ['A', 'B', 'C'],
            'holdings': ['   ', '\t\n', '[{"ticker": "AAPL"}]']
        })
        config = {'column': 'holdings'}

        result = self.expander.execute(config, {}, df)

        expected = pd.DataFrame({
            'portfolio': ['A', 'B', 'C'],
            'ticker': [None, None, 'AAPL']
        })
        pd.testing.assert_frame_equal(result, expected)

    def test_missing_config_error(self):
        """Test error when config is None"""
        with self.assertRaises(ValueError) as context:
            self.expander.execute(None, {}, pd.DataFrame())

        self.assertIn("Configuration is required", str(context.exception))

    def test_missing_column_config_error(self):
        """Test error when column is not specified in config"""
        config = {
            "config": {}
        }

        data = pd.DataFrame({
            "identifier": ["PORTFOLIO1"],
            "holdings": ['[{"cusip": "12345"}]']
        })

        with self.assertRaises(ValueError) as context:
            self.expander.execute(config, {}, data)

        self.assertIn("Column configuration not found", str(context.exception))

    def test_nested_config_structure(self):
        """Test handling of nested config structure"""
        config = {
            "type": "json_array_expander",
            "config": {
                "column": "holdings",
                "include_columns": ["cusip", "holdingPercent"]
            }
        }

        data = pd.DataFrame({
            "identifier": ["PORTFOLIO1"],
            "holdings": ['[{"cusip": "12345", "holdingPercent": 0.15}]']
        })

        result = self.expander.execute(config, {}, data)

        expected = pd.DataFrame({
            "identifier": ["PORTFOLIO1"],
            "cusip": ["12345"],
            "holdingPercent": [0.15]
        })

        pd.testing.assert_frame_equal(result.sort_index(axis=1), expected.sort_index(axis=1))

    def test_flat_config_structure(self):
        """Test handling of flat config structure (legacy support)"""
        config = {
            "column": "holdings",
            "include_columns": ["cusip", "holdingPercent"]
        }

        data = pd.DataFrame({
            "identifier": ["PORTFOLIO1"],
            "holdings": ['[{"cusip": "12345", "holdingPercent": 0.15}]']
        })

        result = self.expander.execute(config, {}, data)

        expected = pd.DataFrame({
            "identifier": ["PORTFOLIO1"],
            "cusip": ["12345"],
            "holdingPercent": [0.15]
        })

        pd.testing.assert_frame_equal(result.sort_index(axis=1), expected.sort_index(axis=1))

    def test_include_columns_dict_mapping(self):
        """Test expansion with include_columns as dictionary mapping JSON keys to custom column names"""
        config = {
            "config": {
                "column": "subjects",
                "include_columns": {
                    "subject": "subject_name",
                    "marks": "score",
                    "grade": "letter_grade",
                    "semester": "term"
                }
            }
        }

        data = pd.DataFrame({
            "student_id": ["STU001"],
            "subjects": [
                '[{"subject": "Math", "marks": 85, "grade": "A", "semester": "Fall"}, {"subject": "Science", "marks": 92, "grade": "A+", "semester": "Fall"}]'
            ]
        })

        result = self.expander.execute(config, {}, data)

        expected = pd.DataFrame({
            "student_id": ["STU001", "STU001"],
            "subject_name": ["Math", "Science"],
            "score": [85, 92],
            "letter_grade": ["A", "A+"],
            "term": ["Fall", "Fall"]
        })

        pd.testing.assert_frame_equal(result.sort_index(axis=1), expected.sort_index(axis=1))

    def test_include_columns_dict_mapping_partial(self):
        """Test expansion with include_columns dict mapping only some keys"""
        config = {
            "config": {
                "column": "subjects",
                "include_columns": {
                    "subject": "subject_name",
                    "marks": "score"
                    # Note: grade and semester are not included
                }
            }
        }

        data = pd.DataFrame({
            "student_id": ["STU001"],
            "subjects": [
                '[{"subject": "Math", "marks": 85, "grade": "A", "semester": "Fall"}]'
            ]
        })

        result = self.expander.execute(config, {}, data)

        expected = pd.DataFrame({
            "student_id": ["STU001"],
            "subject_name": ["Math"],
            "score": [85]
        })

        pd.testing.assert_frame_equal(result.sort_index(axis=1), expected.sort_index(axis=1))

    def test_performance_large_dataset(self):
        """Test performance with a moderately large dataset."""
        import time

        # Create a dataset with 1000 rows
        portfolios = [f'Portfolio_{i}' for i in range(1000)]
        holdings_data = ['[{"ticker": "AAPL", "weight": 0.3}, {"ticker": "GOOGL", "weight": 0.7}]'] * 1000

        df = pd.DataFrame({
            'portfolio': portfolios,
            'holdings': holdings_data,
            'extra_col': ['extra_data'] * 1000
        })

        config = {'column': 'holdings'}

        start_time = time.time()
        result = self.expander.execute(config, {}, df)
        end_time = time.time()

        # Should complete in reasonable time (less than 5 seconds)
        self.assertLess(end_time - start_time, 5.0)

        # Should have 2000 rows (2 holdings per portfolio * 1000 portfolios)
        self.assertEqual(len(result), 2000)

        # Should have correct columns
        expected_columns = {'portfolio', 'extra_col', 'ticker', 'weight'}
        self.assertEqual(set(result.columns), expected_columns)


if __name__ == '__main__':
    unittest.main()
