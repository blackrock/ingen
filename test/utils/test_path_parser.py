#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from datetime import date
from unittest.mock import Mock, ANY

from ingen.utils.path_parser import PathParser


class MyTestCase(unittest.TestCase):

    def test_parse_date_in_path(self):
        date_format = "%d%m%Y"
        today = date.today()
        path = f"/some/path/file_name_$date({date_format}).csv"
        expected_path = f"/some/path/file_name_{today.strftime(date_format)}.csv"

        parser = PathParser(today)
        parsed_path = parser.parse(path)

        self.assertEqual(expected_path, parsed_path)

    def test_default_date_in_path(self):
        date_format = "%d%m%Y"
        today = date.today()
        path = f"/some/path/file_name_$date({date_format}).csv"
        expected_path = f"/some/path/file_name_{today.strftime(date_format)}.csv"

        parser = PathParser()
        parsed_path = parser.parse(path)

        self.assertEqual(expected_path, parsed_path)

    def test_parse_path_with_date_params(self):
        date_format = '%m%d%y'
        today = date.today()
        path = f'file_name_$date({date_format}).csv'
        expected_path = f'file_name_{today.strftime(date_format)}.csv'
        path_parser = PathParser(today)
        formatted_path = path_parser.parse(path)
        self.assertEqual(expected_path, formatted_path)

    def test_interpolator_is_called(self):
        mock_interpolator = Mock()
        path = "/some/path"
        path_parser = PathParser(interpolator=mock_interpolator)
        path_parser.parse(path)
        mock_interpolator.interpolate.assert_called_with(path, ANY)


class TestPathParserOverrideParams(unittest.TestCase):
    """Test PathParser override_params and strict_overrides support."""

    def setUp(self):
        self.test_date = date(2026, 2, 16)

    def test_parse_with_override_params_arg(self):
        """Test parsing path with $override() using override_params argument."""
        override_params = {'FILE_NAME': 'test_file'}
        parser = PathParser(run_date=self.test_date, override_params=override_params)
        result = parser.parse("/path/$override(FILE_NAME).csv")
        self.assertEqual(result, "/path/test_file.csv")

    def test_interpolator_created_with_override_params(self):
        """Test Interpolator is created with params when override_params provided."""
        override_params = {'FILE': '/test.csv'}
        parser = PathParser(override_params=override_params)
        self.assertIsNotNone(parser.interpolator)
        self.assertEqual(parser.interpolator.params, {'override_params': override_params})

    def test_interpolator_created_without_override_params(self):
        """Test Interpolator is created without params when no override_params."""
        parser = PathParser()
        self.assertIsNotNone(parser.interpolator)
        self.assertIsNone(parser.interpolator.params)

    def test_custom_interpolator_takes_precedence(self):
        """Test custom interpolator takes precedence over override_params."""
        from ingen.utils.interpolators.Interpolator import Interpolator
        custom_interpolator = Mock(spec=Interpolator)
        override_params = {'FILE': '/test.csv'}
        parser = PathParser(override_params=override_params, interpolator=custom_interpolator)
        self.assertIs(parser.interpolator, custom_interpolator)

    def test_default_instances_do_not_share_interpolator(self):
        """Test PathParser() gets a fresh Interpolator per instance and $date still works."""
        parser_one = PathParser()
        parser_two = PathParser()
        self.assertIsNot(parser_one.interpolator, parser_two.interpolator)
        result = PathParser(run_date=self.test_date).parse('/path/file_$date(%Y%m%d).csv')
        self.assertEqual(result, '/path/file_20260216.csv')

    def test_parse_override_key_with_params(self):
        """Test $override(KEY) resolves to the value supplied via override_params."""
        parser = PathParser(run_date=self.test_date,
                            override_params={'CMS_CLIENT': 'DYNASTY'},
                            strict_overrides=True)
        result = parser.parse('/p/$override(CMS_CLIENT)_MODEL_INFO.csv')
        self.assertEqual(result, '/p/DYNASTY_MODEL_INFO.csv')

    def test_parse_override_combined_with_date(self):
        """Test $override() combined with $date() adjacent and inside the file name."""
        parser = PathParser(run_date=self.test_date,
                            override_params={'CMS_CLIENT': 'DYNASTY'},
                            strict_overrides=True)
        path = '/d0/aw-cms/$date(%Y%m%d)/$override(CMS_CLIENT)_MODEL_INFO_$date(%Y%m%d).csv'
        result = parser.parse(path)
        self.assertEqual(result, '/d0/aw-cms/20260216/DYNASTY_MODEL_INFO_20260216.csv')

    def test_parse_override_adjacent_to_date(self):
        """Test fully adjacent $override()$date() tokens."""
        parser = PathParser(run_date=self.test_date,
                            override_params={'CMS_CLIENT': 'DYNASTY'},
                            strict_overrides=True)
        result = parser.parse('$override(CMS_CLIENT)$date(%Y%m%d).csv')
        self.assertEqual(result, 'DYNASTY20260216.csv')

    def test_parse_override_combined_with_token(self):
        """Test $override() combined with $token() in the same path."""
        from unittest.mock import patch
        from ingen.utils.interpolators.common_interpolators import COMMON_INTERPOLATORS
        with patch.dict(COMMON_INTERPOLATORS, {'token': lambda *args: '/u1/ftp'}):
            parser = PathParser(run_date=self.test_date,
                                override_params={'CMS_CLIENT': 'DYNASTY'},
                                strict_overrides=True)
            result = parser.parse('$token(FTP_DIR)/$override(CMS_CLIENT)_$date(%Y%m%d).csv')
        self.assertEqual(result, '/u1/ftp/DYNASTY_20260216.csv')

    def test_strict_override_missing_key_raises(self):
        """Test strict mode raises ValueError when the $override key is not supplied."""
        parser = PathParser(run_date=self.test_date,
                            override_params={'OTHER_KEY': 'x'},
                            strict_overrides=True)
        with self.assertRaises(ValueError) as ctx:
            parser.parse('/p/$override(CMS_CLIENT)_MODEL_INFO.csv')
        self.assertIn('CMS_CLIENT', str(ctx.exception))
        self.assertIn('--override_params', str(ctx.exception))

    def test_strict_override_no_override_params_raises(self):
        """Test strict mode raises ValueError when override_params is None and path uses $override."""
        parser = PathParser(run_date=self.test_date, strict_overrides=True)
        with self.assertRaises(ValueError) as ctx:
            parser.parse('/p/$override(CMS_CLIENT)_MODEL_INFO.csv')
        self.assertIn('CMS_CLIENT', str(ctx.exception))

    def test_strict_override_multiple_missing_keys_all_listed(self):
        """Test strict mode error message lists all missing keys."""
        parser = PathParser(run_date=self.test_date,
                            override_params={'A': 'x'},
                            strict_overrides=True)
        with self.assertRaises(ValueError) as ctx:
            parser.parse('/p/$override(A)_$override(B).csv')
        self.assertIn('B', str(ctx.exception))

    def test_non_strict_missing_key_returns_empty(self):
        """Test default non-strict mode keeps existing behaviour (empty string for missing key)."""
        parser = PathParser(run_date=self.test_date, override_params={'A': 'x'})
        result = parser.parse('/p/$override(B)_file.csv')
        self.assertEqual(result, '/p/_file.csv')

    def test_strict_no_override_in_path_parses(self):
        """Test strict mode parses normally when the path has no $override tokens."""
        parser = PathParser(run_date=self.test_date, strict_overrides=True)
        result = parser.parse('/path/file_$date(%Y%m%d).csv')
        self.assertEqual(result, '/path/file_20260216.csv')

    def test_strict_override_empty_value_raises(self):
        """Test strict mode treats an empty override value as missing."""
        parser = PathParser(run_date=self.test_date,
                            override_params={'CMS_CLIENT': ''},
                            strict_overrides=True)
        with self.assertRaises(ValueError) as ctx:
            parser.parse('/p/$override(CMS_CLIENT)_MODEL_INFO.csv')
        self.assertIn('CMS_CLIENT', str(ctx.exception))
        self.assertIn('--override_params', str(ctx.exception))

    def test_strict_override_whitespace_value_raises(self):
        """Test strict mode treats a whitespace-only override value as missing."""
        parser = PathParser(run_date=self.test_date,
                            override_params={'CMS_CLIENT': '   '},
                            strict_overrides=True)
        with self.assertRaises(ValueError) as ctx:
            parser.parse('/p/$override(CMS_CLIENT)_MODEL_INFO.csv')
        self.assertIn('CMS_CLIENT', str(ctx.exception))

    def test_strict_override_parent_dir_values_raise(self):
        """Test strict mode rejects override values containing '..'."""
        for value in ('../x', '..', 'a/../b', 'a\\..\\b'):
            with self.subTest(value=value):
                parser = PathParser(run_date=self.test_date,
                                    override_params={'CMS_CLIENT': value},
                                    strict_overrides=True)
                with self.assertRaises(ValueError) as ctx:
                    parser.parse('/p/$override(CMS_CLIENT)_file.csv')
                self.assertIn('CMS_CLIENT', str(ctx.exception))
                self.assertIn('..', str(ctx.exception))

    def test_strict_override_path_values_allowed(self):
        """Test strict mode allows '/' and '\\' in override values (dirs, full paths)."""
        cases = [
            ('$override(MODEL_INFO_PATH)',
             {'MODEL_INFO_PATH': '/d0/out/DYNASTY_MODEL_INFO.csv'},
             '/d0/out/DYNASTY_MODEL_INFO.csv'),
            ('$override(OUT_DIR)/$override(CMS_CLIENT)_MODEL_INFO_$date(%Y%m%d).csv',
             {'OUT_DIR': '/d0/prod1/reports/aw-cms', 'CMS_CLIENT': 'DYNASTY'},
             '/d0/prod1/reports/aw-cms/DYNASTY_MODEL_INFO_20260216.csv'),
            ('/p/$override(CMS_CLIENT)_file.csv',
             {'CMS_CLIENT': 'a\\b'},
             '/p/a\\b_file.csv'),
        ]
        for path, override_params, expected in cases:
            with self.subTest(path=path):
                parser = PathParser(run_date=self.test_date,
                                    override_params=override_params,
                                    strict_overrides=True)
                self.assertEqual(parser.parse(path), expected)

    def test_strict_override_single_dot_value_allowed(self):
        """Test strict mode allows a value containing a single dot."""
        parser = PathParser(run_date=self.test_date,
                            override_params={'CMS_CLIENT': 'DYN.ASTY'},
                            strict_overrides=True)
        result = parser.parse('/p/$override(CMS_CLIENT)_file.csv')
        self.assertEqual(result, '/p/DYN.ASTY_file.csv')

    def test_non_strict_path_separator_value_resolves(self):
        """Test non-strict mode does not reject path values (other callers unchanged)."""
        parser = PathParser(run_date=self.test_date,
                            override_params={'CMS_CLIENT': '../x'})
        result = parser.parse('/p/$override(CMS_CLIENT)_file.csv')
        self.assertEqual(result, '/p/../x_file.csv')

    def test_non_strict_empty_value_resolves_empty(self):
        """Test non-strict mode resolves an empty override value to empty string."""
        parser = PathParser(run_date=self.test_date,
                            override_params={'CMS_CLIENT': ''})
        result = parser.parse('/p/$override(CMS_CLIENT)_file.csv')
        self.assertEqual(result, '/p/_file.csv')


if __name__ == '__main__':
    unittest.main()
