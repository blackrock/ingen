#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pytest

from ingen.utils.interpolators.common_interpolators import *


class TestCommonInterpolators:

    def test_token_secret_missing_token(self, monkeypatch):
        token_name = 'UNKNOWN_TOKEN'
        
        class PropertiesStub:
            @staticmethod
            def get_property(token):
                return None
        
        monkeypatch.setattr('ingen.utils.interpolators.common_interpolators.Properties', PropertiesStub)
        
        with pytest.raises(ValueError, match=f"'{token_name}' not found"):
            token_secret(token_name)

    def test_timestamp_interpolator(self, monkeypatch):
        format = '%d-%m-%Y %H:%M:%S'
        mock_datetime_obj = datetime.now()
        
        class DateTimeStub:
            def __init__(self):
                self.strftime_calls = []
            
            def strftime(self, fmt):
                self.strftime_calls.append(fmt)
                return mock_datetime_obj
        
        class DateTimeModuleStub:
            def __init__(self):
                self.dt_stub = DateTimeStub()
            
            def now(self):
                return self.dt_stub
        
        datetime_stub = DateTimeModuleStub()
        monkeypatch.setattr('ingen.utils.interpolators.common_interpolators.datetime', datetime_stub)

        actual_result = timestamp(format)
        assert format in datetime_stub.dt_stub.strftime_calls
        assert actual_result == mock_datetime_obj

    def test_uuid(self, monkeypatch):
        mock_uuid_obj = uuid.uuid4()
        
        class UuidStub:
            def uuid4(self):
                return mock_uuid_obj
        
        monkeypatch.setattr('ingen.utils.interpolators.common_interpolators.uuid', UuidStub())

        actual_uuid = uuid_func()
        assert actual_uuid == str(mock_uuid_obj)

    def test_infile(self, monkeypatch):
        mock_filename = 'mlone_restrictions01.xlsx'
        params = {'query_params': None, 'run_date': '09262022', 'infile': 'mlone_restrictions01.xlsx'}

        def mock_get_infile(self, params):
            return mock_filename
        
        monkeypatch.setattr('ingen.utils.interpolators.common_interpolators.get_infile', mock_get_infile)

        actual_filename = get_infile(self, params)
        assert actual_filename == mock_filename
