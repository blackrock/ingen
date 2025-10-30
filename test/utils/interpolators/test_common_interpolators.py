#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from unittest.mock import patch, Mock

import os
from unittest import mock
from ingen.utils.interpolators.common_interpolators import *


class MyTestCase(unittest.TestCase):

    @patch('ingen.utils.interpolators.common_interpolators.Properties')
    def test_token_secret_missing_token(self, mock_properties):
        token_name = 'UNKNOWN_TOKEN'
        mock_properties.get_property.return_value = None
        with self.assertRaisesRegex(ValueError, f"'{token_name}' not found"):
            token_secret(token_name)

    @patch('ingen.utils.interpolators.common_interpolators.datetime')
    def test_timestamp_interpolator(self, mock_datetime):
        format = '%d-%m-%Y %H:%M:%S'
        mock_datetime_obj = datetime.now()
        mock_dt = Mock()
        mock_dt.strftime.return_value = mock_datetime_obj
        mock_datetime.now.return_value = mock_dt

        actual_result = timestamp(format)
        mock_dt.strftime.assert_called_with(format)
        self.assertEqual(mock_datetime_obj, actual_result)

    def test_uuid(self):
        # Import the function directly to test it
        from ingen.utils.interpolators.common_interpolators import uuid_func
        
        # Call the function
        result = uuid_func()
        
        # Verify the result is a string
        self.assertIsInstance(result, str)
        
        # Check if it's a valid UUID (with or without hyphens)
        import re
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}$', re.I)
        self.assertTrue(bool(uuid_pattern.match(result)), 
                       f"{result} is not a valid UUID (with or without hyphens)")

    def test_get_infile_simple(self):
        # Test with simple filename
        params = {'infile': '/path/to/file.txt'}
        result = get_infile(None, params)
        self.assertEqual('file.txt', result)

    def test_get_infile_with_key(self):
        # Test with key-value mapping
        params = {'infile': {'source1': '/path/to/file1.txt', 'source2': '/path/to/file2.txt'}}
        result = get_infile('source1', params)
        self.assertEqual('file1.txt', result)

    def test_get_infile_missing_key(self):
        # Test with missing key in mapping
        params = {'infile': {'source1': '/path/to/file1.txt'}}
        with self.assertRaises(KeyError):
            get_infile('nonexistent', params)

    def test_get_infile_no_params(self):
        # Test with no params
        self.assertEqual('', get_infile(None, None))

    def test_get_infile_empty_params(self):
        # Test with empty params
        self.assertEqual('', get_infile(None, {}))

    def test_get_overrides_found(self):
        # Test getting an existing override
        params = {'override_params': {'key1': 'value1', 'key2': 'value2'}}
        result = get_overrides('key1', params)
        self.assertEqual('value1', result)

    def test_get_overrides_not_found(self):
        # Test getting a non-existent override
        params = {'override_params': {'key1': 'value1'}}
        result = get_overrides('nonexistent', params)
        self.assertEqual('', result)

    def test_get_overrides_no_params(self):
        # Test with no params
        self.assertEqual('', get_overrides('key', None))

    def test_get_overrides_empty_params(self):
        # Test with empty params
        self.assertEqual('', get_overrides('key', {}))


if __name__ == '__main__':
    unittest.main()
