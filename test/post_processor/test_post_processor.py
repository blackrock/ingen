import unittest

import pandas as pd

from ingen.post_processor.common_post_processor import pivot_to_dynamic_columns
from ingen.post_processor.post_processor import PostProcessor

class TestPostProcessor(unittest.TestCase):

    def setUp(self):
        # Sample dataframe
        self.data = {
            'model_id': ['1', '2', '3'],
            'name': ['model_1', 'model_2', 'model_3'],
            'defn_name': ['RISK_PROFILE', 'REGION', ''],
            'defn_value': ['Aggressive', 'US', '']
        }
        self.df = pd.DataFrame(self.data)

        # Sample post-process configuration
        self.post_processes = [{
            "type": "pivot",
            "processing_values": {
                "pivot_col": "defn_name",
                "value_col": "defn_value"
            }
        }]

    def test_init_with_valid_dataframe(self):
        # Test that initialization with a valid dataframe works
        processor = PostProcessor(self.post_processes, self.df)
        self.assertEqual(processor._formatted_data.shape, self.df.shape)

    def test_init_with_invalid_data(self):
        # Test that non-dataframe input raises a TypeError
        processor = PostProcessor(self.post_processes, "invalid_input")
        with self.assertRaises(TypeError):
            processor.apply_post_processing()

    def test_init_with_empty_dataframe(self):
        # Test that empty dataframe raises a ValueError
        processor = PostProcessor(self.post_processes, pd.DataFrame())
        with self.assertRaises(ValueError):
            processor.apply_post_processing()

    def test_get_processor_func_valid(self):
        # Test that the correct function is returned for valid post-processing type
        processor = PostProcessor(self.post_processes, self.df)
        func = processor.get_processor_func(self.post_processes[0])
        self.assertEqual(func, pivot_to_dynamic_columns)

    def test_get_processor_func_invalid(self):
        # Test that invalid post-processing type raises a NameError
        invalid_post_process = [{
            "type": "invalid_type",
            "processing_values": {}
        }]
        processor = PostProcessor(invalid_post_process, self.df)
        with self.assertRaises(NameError):
            processor.get_processor_func(invalid_post_process[0])

if __name__ == '__main__':
    unittest.main()