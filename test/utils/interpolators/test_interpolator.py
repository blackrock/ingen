import unittest
from unittest.mock import patch

from ingen.utils.interpolators.Interpolator import Interpolator


def sample_interpolator_function(arg, params=None):
    return "replaced_value"


def mock_get_property(token, params=None):
    return "mocked_token_value"


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.interpolator = Interpolator()

    def test_interpolation(self):
        string_val = "a_$sample_interpolator_function(sample_arg)_b"
        expected_val = "a_replaced_value_b"
        function_map = {
            'sample_interpolator_function': sample_interpolator_function
        }
        parsed_str = self.interpolator.interpolate(string_val, function_map)
        self.assertEqual(expected_val, parsed_str)

    def test_interpolation_when_method_not_found(self):
        string_val = "a_$unknown_function(sample_arg)_b"
        with self.assertRaisesRegex(KeyError, "No interpolator function found for 'unknown_function'"):
            function_map = {}
            self.interpolator.interpolate(string_val, function_map)

    def test_interpolation_with_two_replaceable_items(self):
        string_val = "a_$sample_interpolator_function(sample_arg)_b_$sample_interpolator_function(sample_arg)_c"
        expected_val = "a_replaced_value_b_replaced_value_c"
        function_map = {
            'sample_interpolator_function': sample_interpolator_function
        }
        parsed_str = self.interpolator.interpolate(string_val, function_map)
        self.assertEqual(expected_val, parsed_str)

    @patch('ingen.utils.interpolators.Interpolator.COMMON_INTERPOLATORS', {'token': mock_get_property})
    def test_interpolation_with_common_interpolator_and_custom_interpolator(self):
        string_val = "$token(sample_token)__$sample_interpolator_function(sample_arg)__"
        expected_val = "mocked_token_value__replaced_value__"
        function_map = {
            'sample_interpolator_function': sample_interpolator_function
        }
        parsed_str = self.interpolator.interpolate(string_val, function_map)
        self.assertEqual(expected_val, parsed_str)


if __name__ == '__main__':
    unittest.main()
