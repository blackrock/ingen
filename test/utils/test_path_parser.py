#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from datetime import date

from ingen.utils.path_parser import PathParser


class TestPathParser:

    def test_parse_date_in_path(self):
        date_format = "%d%m%Y"
        today = date.today()
        path = f"/some/path/file_name_$date({date_format}).csv"
        expected_path = f"/some/path/file_name_{today.strftime(date_format)}.csv"

        parser = PathParser(today)
        parsed_path = parser.parse(path)

        assert parsed_path == expected_path

    def test_default_date_in_path(self):
        date_format = "%d%m%Y"
        today = date.today()
        path = f"/some/path/file_name_$date({date_format}).csv"
        expected_path = f"/some/path/file_name_{today.strftime(date_format)}.csv"

        parser = PathParser()
        parsed_path = parser.parse(path)

        assert parsed_path == expected_path

    def test_parse_path_with_date_params(self):
        date_format = '%m%d%y'
        today = date.today()
        path = f'file_name_$date({date_format}).csv'
        expected_path = f'file_name_{today.strftime(date_format)}.csv'
        path_parser = PathParser(today)
        formatted_path = path_parser.parse(path)
        assert formatted_path == expected_path

    def test_interpolator_is_called(self):
        class InterpolatorStub:
            def __init__(self):
                self.interpolate_calls = []
            
            def interpolate(self, path, function_map):
                self.interpolate_calls.append((path, function_map))
                return path
        
        interpolator_stub = InterpolatorStub()
        path = "/some/path"
        path_parser = PathParser(interpolator=interpolator_stub)
        path_parser.parse(path)
        
        assert len(interpolator_stub.interpolate_calls) == 1
        assert interpolator_stub.interpolate_calls[0][0] == path
