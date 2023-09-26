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


if __name__ == '__main__':
    unittest.main()
