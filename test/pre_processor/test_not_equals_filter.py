import unittest 
import pandas as pd

from ingen.pre_processor.not_equals_filter import NotEqualsFilter

class TestNotEqualsFilter(unittest.TestCase):

    def setUp(self):
        self.filter = NotEqualsFilter()
        self.sample_data = pd.DataFrame({
            "id": ['user1', 'user2', 'user3', 'user4', 'user5'],
            "SYSTEM": ['SYS_A', 'SYS_A', 'SYS_B', 'SYS_B', 'SYS_C'],
            "email": ['user1@example.com', 'user2@example.com', 'user3@example.com', 'user4@example.com', 'user5@example.com']
        })
        
    def test_not_equals_filter_single_value(self):
        """Test filtering out rows where SYSTEM is SYS_A"""
        config = {
            "cols": [
                {"col": "SYSTEM", "val": ["SYS_A"]}
            ]
        }
        result = self.filter.execute(config, {}, self.sample_data)
        self.assertEqual(len(result), 3)
        self.assertListEqual(result["id"].tolist(), ["user3", "user4", "user5"])

    def test_not_equals_filter_multiple_values(self):
        """Test filtering out rows where SYSTEM is SYS_A or SYS_B"""
        config = {
            "cols": [
                {"col": "SYSTEM", "val": ["SYS_A", "SYS_B"]}
            ]
        }
        result = self.filter.execute(config, {}, self.sample_data)
        self.assertEqual(len(result), 2)
        self.assertListEqual(result["id"].tolist(), ["user5"])
    
    def test_not_equals_filter_empty_dataframe(self):
         """Test with empty DataFrame"""
         config = {
             "cols": [
                 {"col": "SYSTEM", "val": ["SYS_A"]}
             ]
         }
         empty_df = pd.DataFrame()
         
         result = self.filter.execute(config, {}, empty_df)

         self.assertEqual(result.empty, True)
