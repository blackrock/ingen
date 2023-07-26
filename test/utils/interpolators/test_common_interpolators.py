import unittest
from unittest.mock import patch, Mock

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

    @patch('ingen.utils.interpolators.common_interpolators.uuid')
    def test_uuid(self, mock_uuid):
        mock_uuid_obj = uuid.uuid4()
        mock_uuid.uuid4.return_value = mock_uuid_obj

        actual_uuid = uuid_func()
        self.assertEqual(str(mock_uuid_obj), actual_uuid)

    @patch('ingen.utils.interpolators.common_interpolators.get_infile')
    def test_infile(self, params):
        mock_filename = 'mlone_restrictions01.xlsx'
        params = {'query_params': None, 'run_date': '09262022', 'infile': 'mlone_restrictions01.xlsx'}

        actual_filename = get_infile(self, params)
        self.assertEqual(mock_filename, actual_filename)


if __name__ == '__main__':
    unittest.main()
