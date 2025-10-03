import pytest
import numpy as np
import pandas as pd

from ingen.post_processor.common_post_processor import pivot_to_dynamic_columns


class TestCommonPostProcessors:

    def test_pivot_to_dynamic_columns(self):
        data = {
            'model_id': [1, 1, 2, 2, 3],
            'name': ['TEST_1', 'TEST_1', 'TEST_2', 'TEST_2', 'TEST_3'],
            'defn_name': ['RISK_PROFILE', 'REGION', 'RISK_PROFILE', 'REGION', np.nan],
            'defn_value': ['Aggressive', 'US', 'Conservative', 'EMEA', np.nan]
        }
        dataframe = pd.DataFrame(data)

        # Expected output DataFrame after transformation
        expected_data = {
            'model_id': [1, 2, 3],
            'name': ['TEST_1', 'TEST_2', 'TEST_3'],
            'RISK_PROFILE': ['Aggressive', 'Conservative', np.nan],
            'REGION': ['US', 'EMEA', np.nan]
        }
        expected_df = pd.DataFrame(expected_data)
        param = {
            'pivot_col': 'defn_name',
            'value_col': 'defn_value'
        }

        result_df = pivot_to_dynamic_columns(dataframe, param)
        expected_df = expected_df.sort_index(axis=1)
        result_df = result_df.sort_index(axis=1)
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_pivot_with_missing_values(self):
        data = {
            'model_id': ['1', '1', '2', '2', '3', '3', '4'],
            'name': ['MODEL_1', 'MODEL_1', 'MODEL_2', 'MODEL_2', 'MODEL_3', 'MODEL_3', 'MODEL_4'],
            'defn_name': ['RISK_PROFILE', 'REGION', 'RISK_PROFILE', 'REGION', 'RISK_PROFILE', np.nan, 'REGION'],
            'defn_value': ['Aggressive', 'US', 'Conservative', 'AUS', 'Moderate', np.nan, 'EMEA']
        }
        dataframe = pd.DataFrame(data)

        # Expected output after transformation
        expected_data = {
            'model_id': ['1', '2', '3', '4'],
            'name': ['MODEL_1', 'MODEL_2', 'MODEL_3', 'MODEL_4'],
            'RISK_PROFILE': ['Aggressive', 'Conservative', 'Moderate', np.nan],
            'REGION': ['US', 'AUS', np.nan, 'EMEA']
        }
        expected_df = pd.DataFrame(expected_data)

        param = {
            'pivot_col': 'defn_name',
            'value_col': 'defn_value'
        }

        result_df = pivot_to_dynamic_columns(dataframe, param)
        expected_df = expected_df.sort_index(axis=1)
        result_df = result_df.sort_index(axis=1)
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_pivot_to_dynamic_columns_with_missing_values(self):
        data = {
            'model_id': ['1', '1', '2', '2'],
            'name': ['MODEL_1', 'MODEL_1', 'MODEL_2', 'MODEL_2'],
            'defn_value': ['Aggressive', 'US', 'Conservative', 'EMEA']  # 'defn_name' is missing
        }
        dataframe = pd.DataFrame(data)

        config = {
            'pivot_col': 'defn_name',
            'value_col': 'defn_value'
        }

        # Attempt to call the function with a missing 'defn_name' column
        with pytest.raises(KeyError, match=r"Column defn_name not found\."):
            pivot_to_dynamic_columns(dataframe, config)

    def test_pivot_to_dynamic_columns_with_missing_value_col(self):
        data = {
            'model_id': ['1', '1', '2', '2'],
            'name': ['MODEL_1', 'MODEL_1', 'MODEL_2', 'MODEL_2'],
            'defn_name': ['RISK_PROFILE', 'REGION', 'RISK_PROFILE', 'REGION'],
        }
        dataframe = pd.DataFrame(data)

        config = {
            'pivot_col': 'defn_name',
            'value_col': 'defn_value'
        }

        # Attempt to call the function with a missing 'defn_value' column
        with pytest.raises(KeyError, match=r"Column defn_value not found\."):
            pivot_to_dynamic_columns(dataframe, config)
