#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from unittest.mock import MagicMock, call

import pandas as pd

from ingen.reader.snowflake_reader import DEFAULT_BATCH_SIZE, SnowflakeReader


class TestSnowflakeReader(unittest.TestCase):

    def setUp(self):
        self.connection = MagicMock()
        self.cursor = self.connection.cursor.return_value.__enter__.return_value
        self.cursor.description = [('COL1',), ('COL2',)]

    def test_execute_returns_dataframe(self):
        self.cursor.fetchmany.side_effect = [[('a', 1), ('b', 2)], []]

        result = SnowflakeReader(self.connection).execute('select * from SAMPLE_TABLE')

        pd.testing.assert_frame_equal(result, pd.DataFrame({'COL1': ['a', 'b'], 'COL2': [1, 2]}))
        self.cursor.execute.assert_called_once_with('select * from SAMPLE_TABLE')
        self.cursor.fetchmany.assert_called_with(DEFAULT_BATCH_SIZE)
        self.connection.close.assert_called_once()

    def test_execute_fetches_in_batches(self):
        self.cursor.fetchmany.side_effect = [[('a', 1), ('b', 2)], [('c', 3)], []]

        result = SnowflakeReader(self.connection, batch_size=2).execute('select * from SAMPLE_TABLE')

        pd.testing.assert_frame_equal(result, pd.DataFrame({'COL1': ['a', 'b', 'c'], 'COL2': [1, 2, 3]}))
        self.assertEqual([call(2)] * 3, self.cursor.fetchmany.call_args_list)
        self.cursor.fetchall.assert_not_called()

    def test_execute_empty_result_keeps_columns(self):
        self.cursor.fetchmany.side_effect = [[]]

        result = SnowflakeReader(self.connection).execute('select * from EMPTY_TABLE')

        self.assertTrue(result.empty)
        self.assertEqual(['COL1', 'COL2'], list(result.columns))

    def test_query_logged_at_debug_level(self):
        self.cursor.fetchmany.side_effect = [[]]

        with self.assertLogs(level='DEBUG') as logs:
            SnowflakeReader(self.connection).execute('select * from SAMPLE_TABLE')

        self.assertIn('DEBUG:root:Running query: select * from SAMPLE_TABLE', logs.output)
        self.assertFalse(any('select' in line for line in logs.output if not line.startswith('DEBUG')))

    def test_connection_closed_on_error(self):
        self.cursor.execute.side_effect = Exception('Query failed')

        with self.assertRaisesRegex(Exception, 'Query failed'):
            SnowflakeReader(self.connection).execute('select * from BAD_TABLE')
        self.connection.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
