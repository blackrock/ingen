# Copyright (c) 2023 BlackRock, Inc.
# All Rights Reserved.
import unittest
from unittest.mock import patch, Mock, call
import pandas as pd
from ingen.reader.mysql_reader import MYSQLReader


class TestMYSQLReader(unittest.TestCase):
    """Test suite for MYSQLReader class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_connection = Mock()
        self.reader = MYSQLReader(self.mock_connection)
        self.test_query = "SELECT * FROM SAMPLE_TABLE"
        self.expected_df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie']
        })
    
    def tearDown(self):
        """Clean up after each test method."""
        self.mock_connection.reset_mock()
    
    @patch("ingen.reader.mysql_reader.pd.read_sql")
    def test_execute_returns_dataframe(self, mock_read_sql):
        """Test that execute returns a DataFrame with correct data."""
        mock_read_sql.return_value = self.expected_df
        
        result = self.reader.execute(self.test_query)
        
        pd.testing.assert_frame_equal(self.expected_df, result)
        
        mock_read_sql.assert_called_once_with(
            self.test_query, 
            self.mock_connection
        )
    
    @patch("ingen.reader.mysql_reader.pd.read_sql")
    def test_execute_with_empty_result(self, mock_read_sql):
        """Test execute handles empty result set correctly."""
        empty_df = pd.DataFrame()
        mock_read_sql.return_value = empty_df
        
        result = self.reader.execute(self.test_query)
        
        pd.testing.assert_frame_equal(empty_df, result)
        self.assertTrue(result.empty)
    
    @patch("ingen.reader.mysql_reader.pd.read_sql")
    def test_execute_with_parameters(self, mock_read_sql):
        """Test execute with parameterized query."""
        mock_read_sql.return_value = self.expected_df
        params = {'id': 1}
        query_with_params = "SELECT * FROM SAMPLE_TABLE WHERE id = %(id)s"
        
        result = self.reader.execute(query_with_params, params)
        
        mock_read_sql.assert_called_once_with(
            query_with_params,
            self.mock_connection,
            params=params
        )
    
    @patch("ingen.reader.mysql_reader.pd.read_sql")
    def test_execute_handles_sql_exception(self, mock_read_sql):
        """Test that execute handles SQL exceptions properly."""
        mock_read_sql.side_effect = Exception("Database connection error")
        
        with self.assertRaises(Exception) as context:
            self.reader.execute(self.test_query)
        
        self.assertIn("Database connection error", str(context.exception))
    
    def test_connection_close(self):
        """Test that connection can be closed properly."""
        self.reader.close()
        self.mock_connection.close.assert_called_once()
    
    @patch("ingen.reader.mysql_reader.pd.read_sql")
    def test_execute_does_not_close_connection(self, mock_read_sql):
        """Test that execute doesn't close the connection prematurely."""
        mock_read_sql.return_value = self.expected_df
        
        self.reader.execute(self.test_query)
        
        self.mock_connection.close.assert_not_called()


if __name__ == '__main__':
    unittest.main()
