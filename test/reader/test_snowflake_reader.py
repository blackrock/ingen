#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from unittest.mock import MagicMock

import pandas as pd

from ingen.reader.snowflake_reader import SnowflakeReader


class TestSnowflakeReader(unittest.TestCase):

    def setUp(self):
        self.connection = MagicMock()
        self.cursor = self.connection.cursor.return_value.__enter__.return_value

    def test_execute_returns_dataframe(self):
        self.cursor.fetchall.return_value = [('a', 1), ('b', 2)]
        self.cursor.description = [('COL1',), ('COL2',)]

        result = SnowflakeReader(self.connection).execute('select * from SAMPLE_TABLE')

        pd.testing.assert_frame_equal(result, pd.DataFrame({'COL1': ['a', 'b'], 'COL2': [1, 2]}))
        self.cursor.execute.assert_called_once_with('select * from SAMPLE_TABLE')
        self.connection.close.assert_called_once()

    def test_execute_empty_result_keeps_columns(self):
        self.cursor.fetchall.return_value = []
        self.cursor.description = [('COL1',), ('COL2',)]

        result = SnowflakeReader(self.connection).execute('select * from EMPTY_TABLE')

        self.assertTrue(result.empty)
        self.assertEqual(['COL1', 'COL2'], list(result.columns))

    def test_connection_closed_on_error(self):
        self.cursor.execute.side_effect = Exception('Query failed')

        with self.assertRaisesRegex(Exception, 'Query failed'):
            SnowflakeReader(self.connection).execute('select * from BAD_TABLE')
        self.connection.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
