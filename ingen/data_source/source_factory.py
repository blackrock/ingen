#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from ingen.data_source.data_source_type import DataSourceType
from ingen.data_source.file_source import FileSource
from ingen.data_source.json_source import JsonSource
from ingen.data_source.mysql_source import MYSQLSource
from ingen.data_source.rawdata_source import RawDataSource


class SourceFactory:
    def parse_source(self, source, params_map, dynamic_data=None):
        if source['type'] == DataSourceType.File.value:
            return FileSource(source, params_map)
        elif source['type'] == DataSourceType.MYSQL.value:
            return MYSQLSource(source)
        elif source['type'] == DataSourceType.Api.value:
            # Conditional import added here to avoid circular dependency
            # API Source -> URL Constructor -> Source Factory -> API Source
            from ingen.data_source.api_source import APISource
            return APISource(source, params_map)
        elif source['type'] == DataSourceType.RawDataStore.value:
            return RawDataSource(source)
        elif source['type'] == DataSourceType.JSON.value:
            return JsonSource(source, dynamic_data)
        else:
            raise ValueError(f"Unknown source type {source.get('type')}.")
