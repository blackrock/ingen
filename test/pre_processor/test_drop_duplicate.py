import unittest

import pandas as pd

from ingen.pre_processor.drop_duplicates import DropDuplicates


class MyTestCase(unittest.TestCase):
    def test_drop_duplicate_on_single_column(self):
        config = {
            'type': 'drop_duplicates',
            'columns': ['name'],
            'keep': 'first'
        }
        data = pd.DataFrame({
            'name': ['Ashish', 'Aman', 'Ashish', 'Aditya', 'Aditya'],
            'marks': [50, 75, 82, 93, 77],
            'subject': ['Science', 'Hindi', 'Hindi', 'English', 'Maths']
        })
        expected_data = pd.DataFrame({
            'name': ['Ashish', 'Aman', 'Aditya'],
            'marks': [50, 75, 93],
            'subject': ['Science', 'Hindi', 'English']
        })

        pre_processor = DropDuplicates()
        actual_data = pre_processor.execute(config, sources_data=[data], data=data)
        pd.testing.assert_frame_equal(expected_data, actual_data)

    def test_drop_duplicates_on_multiple_columns(self):
        config = {
            'type': 'drop_duplicates',
            'columns': ['name', 'subject'],
            'keep': 'first'
        }
        data = pd.DataFrame({
            'name': ['Ashish', 'Ashish', 'Aman', 'Ashish', 'Aditya', 'Aditya'],
            'marks': [50, 30, 75, 82, 93, 77],
            'subject': ['Science', 'Science', 'Hindi', 'Hindi', 'English', 'Maths']
        })
        expected_data = pd.DataFrame({
            'name': ['Ashish', 'Aman', 'Ashish', 'Aditya', 'Aditya'],
            'marks': [50, 75, 82, 93, 77],
            'subject': ['Science', 'Hindi', 'Hindi', 'English', 'Maths']
        })

        pre_processor = DropDuplicates()
        actual_data = pre_processor.execute(config, sources_data=[data], data=data)
        pd.testing.assert_frame_equal(expected_data, actual_data)

    def test_drop_duplicates_on_all_columns(self):
        config = {
            'type': 'drop_duplicates',
            'keep': 'first'
        }
        data = pd.DataFrame({
            'name': ['Ashish', 'Ashish', 'Aman', 'Ashish', 'Aditya', 'Aditya'],
            'marks': [50, 50, 75, 82, 93, 77],
            'subject': ['Science', 'Science', 'Hindi', 'Hindi', 'English', 'Maths']
        })
        expected_data = pd.DataFrame({
            'name': ['Ashish', 'Aman', 'Ashish', 'Aditya', 'Aditya'],
            'marks': [50, 75, 82, 93, 77],
            'subject': ['Science', 'Hindi', 'Hindi', 'English', 'Maths']
        })

        pre_processor = DropDuplicates()
        actual_data = pre_processor.execute(config, sources_data=[data], data=data)
        pd.testing.assert_frame_equal(expected_data, actual_data)

    def test_drop_duplicates_with_default_configs(self):
        # by default duplicates are dropped based on all columns and keeping the first element
        config = {
            'type': 'drop_duplicates'
        }
        data = pd.DataFrame({
            'name': ['Ashish', 'Ashish', 'Aman', 'Ashish', 'Aditya', 'Aditya'],
            'marks': [50, 50, 75, 82, 93, 77],
            'subject': ['Science', 'Science', 'Hindi', 'Hindi', 'English', 'Maths']
        })
        expected_data = pd.DataFrame({
            'name': ['Ashish', 'Aman', 'Ashish', 'Aditya', 'Aditya'],
            'marks': [50, 75, 82, 93, 77],
            'subject': ['Science', 'Hindi', 'Hindi', 'English', 'Maths']
        })

        pre_processor = DropDuplicates()
        actual_data = pre_processor.execute(config, sources_data=[data], data=data)
        pd.testing.assert_frame_equal(expected_data, actual_data)

    def test_drop_last_duplicates(self):
        config = {
            'type': 'drop_duplicates',
            'columns': ['name', 'subject'],
            'keep': 'last'
        }
        data = pd.DataFrame({
            'name': ['Ashish', 'Ashish', 'Aman', 'Ashish', 'Aditya', 'Aditya'],
            'marks': [50, 30, 75, 82, 93, 77],
            'subject': ['Science', 'Science', 'Hindi', 'Hindi', 'English', 'Maths']
        })
        expected_data = pd.DataFrame({
            'name': ['Ashish', 'Aman', 'Ashish', 'Aditya', 'Aditya'],
            'marks': [30, 75, 82, 93, 77],
            'subject': ['Science', 'Hindi', 'Hindi', 'English', 'Maths']
        })

        pre_processor = DropDuplicates()
        actual_data = pre_processor.execute(config, sources_data=[data], data=data)
        pd.testing.assert_frame_equal(expected_data, actual_data)

    def test_drop_all_duplicates(self):
        config = {
            'type': 'drop_duplicates',
            'columns': ['name', 'subject'],
            'keep': False
        }
        data = pd.DataFrame({
            'name': ['Ashish', 'Ashish', 'Aman', 'Ashish', 'Aditya', 'Aditya'],
            'marks': [50, 30, 75, 82, 93, 77],
            'subject': ['Science', 'Science', 'Hindi', 'Hindi', 'English', 'Maths']
        })
        expected_data = pd.DataFrame({
            'name': ['Aman', 'Ashish', 'Aditya', 'Aditya'],
            'marks': [75, 82, 93, 77],
            'subject': ['Hindi', 'Hindi', 'English', 'Maths']
        })

        pre_processor = DropDuplicates()
        actual_data = pre_processor.execute(config, sources_data=[data], data=data)
        pd.testing.assert_frame_equal(expected_data, actual_data)


if __name__ == '__main__':
    unittest.main()
