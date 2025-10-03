#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import os

from ingen.data_source.file_source import FileSource
from ingen.data_source.source_factory import SourceFactory


class TestSourceFactory:

    def test_parse_source_for_file(self, monkeypatch):
        monkeypatch.setenv('FILE_SOURCE', 'test/file/path/name_$date(%d%m%Y).csv')
        environment_var = 'FILE_SOURCE'
        file_source = {
            'id': 'test_id',
            'type': 'file',
            'file_type': 'delimited_file',
            'file_path': f'$${environment_var}'
        }
        params_map = {'query_params': {'table_name': 'positions'}}
        sf = SourceFactory()
        file = sf.parse_source(file_source, params_map)
        assert isinstance(file, FileSource)
        assert file._src == file_source


 
