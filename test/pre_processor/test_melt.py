#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pandas as pd

from ingen.pre_processor.melt import Melt


class TestDFMelt:

    def test_column_to_row_formatter_for_specific_columns(self):
        sample_data = pd.DataFrame({
            'abc': [123],
            'def': [456],
            'ghi': [789],
            'jkl': [1011],
            'mno': [1213],
        })

        expected_data = pd.DataFrame({'TICKER': ['abc', 'def', 'mno'], 'PORTFOLIO_ID': [123, 456, 1213]})
        config = {'type': 'melt', 'source': ['source1'], 'key_column': 'TICKER', 'value_column': 'PORTFOLIO_ID',
                  'include_keys': ['abc', 'def', 'mno']}
        obj = Melt()
        result = obj.execute(config, {'source1': sample_data}, None)
        pd.testing.assert_frame_equal(expected_data.reset_index(drop=True), result.reset_index(drop=True))

    def test_column_to_row_formatter_for_all_columns(self):
        sample_data = pd.DataFrame({
            'Z88336900': [312992],
            'Z88800281': [312876],
            'Z88800293': [312964]
        })

        expected_data = pd.DataFrame({'TICKER': ['Z88336900', 'Z88800281', 'Z88800293'],
                                      'PORTFOLIO_ID': [312992, 312876, 312964],
                                      })

        config = {'type': 'melt', 'source': ['source1'], 'key_column': 'TICKER', 'value_column': 'PORTFOLIO_ID',
                  'include_keys': []}
        obj = Melt()
        result = obj.execute(config, {'source1': sample_data}, None)
        pd.testing.assert_frame_equal(expected_data.reset_index(drop=True), result.reset_index(drop=True))
