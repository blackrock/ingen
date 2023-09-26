#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from unittest.mock import patch, Mock

import pandas as pd

from ingen.reader.mysql_reader import MYSQLReader


class TestDBReader(unittest.TestCase):

    @patch("ingen.reader.mysql_reader.pd")
    def test_execute(self, mock_pandas):
        mock_connection = Mock()
        mock_connection.close.return_value = ""
        reader = MYSQLReader(mock_connection)
        mock_pandas.read_sql.return_value = pd.DataFrame()
        dataframe = reader.execute("select * from SAMPLE_TABLE")
        pd.testing.assert_frame_equal(pd.DataFrame(), dataframe)
