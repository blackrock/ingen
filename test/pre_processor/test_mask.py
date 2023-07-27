import unittest

import pandas as pd

from ingen.pre_processor.mask import Mask


class MyTestCase(unittest.TestCase):
    def test_mask(self):
        positions = pd.DataFrame({'PORTFOLIO_ID': [1, 2, 3, 4, 5], 'CURRENCY': ['USD'] * 5})
        accounts = pd.DataFrame({'ACCOUNT_ID': [1, 2, 5], 'MKT_VALUE': [200, 456.34, 234.56]})

        expected_dataframe = pd.DataFrame({'PORTFOLIO_ID': [1, 2, 5], 'CURRENCY': ['USD'] * 3})

        data = positions
        on_col = 'PORTFOLIO_ID'
        masking_data = accounts
        masking_col = 'ACCOUNT_ID'

        mask = Mask()
        masked_data = mask.mask(data, on_col, masking_col, masking_data)

        pd.testing.assert_frame_equal(expected_dataframe, masked_data, check_index_type=False)

    def test_execute(self):
        positions = pd.DataFrame({'PORTFOLIO_ID': [1, 2, 3, 4, 5], 'CURRENCY': ['USD'] * 5})
        accounts = pd.DataFrame({'ACCOUNT_ID': [1, 2, 5], 'MKT_VALUE': [200, 456.34, 234.56]})

        data = positions
        sources_data = {
            'accounts': accounts
        }
        config = {
            'on_col': 'PORTFOLIO_ID',
            'masking_source': 'accounts',
            'masking_col': 'ACCOUNT_ID'
        }

        expected_dataframe = pd.DataFrame({'PORTFOLIO_ID': [1, 2, 5], 'CURRENCY': ['USD'] * 3})
        mask = Mask()
        masked_data = mask.execute(config, sources_data, data)

        pd.testing.assert_frame_equal(expected_dataframe, masked_data)


if __name__ == '__main__':
    unittest.main()
