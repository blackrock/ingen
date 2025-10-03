#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pandas as pd

from ingen.reader.mysql_reader import MYSQLReader


class MockConnection:
    def close(self):
        return ""


class TestDBReader:

    def test_execute(self, monkeypatch):
        mock_connection = MockConnection()
        reader = MYSQLReader(mock_connection)
        
        class MockPandas:
            @staticmethod
            def read_sql(*args, **kwargs):
                return pd.DataFrame()
        
        mock_pandas = MockPandas()
        monkeypatch.setattr("ingen.reader.mysql_reader.pd", mock_pandas)
        
        dataframe = reader.execute("select * from SAMPLE_TABLE")
        pd.testing.assert_frame_equal(pd.DataFrame(), dataframe)