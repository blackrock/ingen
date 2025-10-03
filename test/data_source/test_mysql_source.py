#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from unittest.mock import Mock

from pandas import DataFrame

from ingen.data_source.data_source_type import DataSourceType
from ingen.data_source.mysql_source import MYSQLSource


class MYSQLSourceTest:

    def setup_method(self):
        self.input_source = {
            'id': 'sample_source',
            'type': DataSourceType.MYSQL.value,
            'host_name': '127.0.0.1',
            'user': 'sample_user',
            'database': 'sample_database',
            'query': 'select * from SAMPLE_TABLE'
        }

    def test_fetch(self, monkeypatch):
        mock_property = Mock(return_value="")
        mock_sql_parser = Mock()
        mock_sql_parser.return_value.parse_query.return_value = "select * from SAMPLE_TABLE"
        mock_connection = Mock()
        mock_reader = Mock()
        mock_reader.return_value.execute.return_value = DataFrame()
        
        monkeypatch.setattr('ingen.data_source.mysql_source.properties', mock_property)
        monkeypatch.setattr('ingen.data_source.mysql_source.SqlQueryParser', mock_sql_parser)
        monkeypatch.setattr('ingen.data_source.mysql_source.pymysql', mock_connection)
        monkeypatch.setattr('ingen.data_source.mysql_source.MYSQLReader', mock_reader)
        
        source = MYSQLSource(self.input_source)
        data = source.fetch()
        assert data.size == 0

    def test_fetch_validations(self, monkeypatch):
        mock_property = Mock(return_value="")
        mock_sql_parser = Mock()
        mock_connection = Mock()
        
        monkeypatch.setattr('ingen.data_source.mysql_source.properties', mock_property)
        monkeypatch.setattr('ingen.data_source.mysql_source.SqlQueryParser', mock_sql_parser)
        monkeypatch.setattr('ingen.data_source.mysql_source.pymysql', mock_connection)
        
        source = MYSQLSource(self.input_source)
        assert len(source.fetch_validations()) == 0
