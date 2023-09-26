import unittest
from unittest.mock import patch

from pandas import DataFrame

from ingen.data_source.data_source_type import DataSourceType
from ingen.data_source.mysql_source import MYSQLSource


class MYSQLSourceTest(unittest.TestCase):

    def setUp(self):
        self.input_source = {
            'id': 'sample_source',
            'type': DataSourceType.MYSQL.value,
            'host_name': '127.0.0.1',
            'user': 'sample_user',
            'database': 'sample_database',
            'query': 'select * from SAMPLE_TABLE'
        }

    @patch('ingen.data_source.mysql_source.MYSQLReader')
    @patch('ingen.data_source.mysql_source.pymysql')
    @patch('ingen.data_source.mysql_source.SqlQueryParser')
    @patch('ingen.data_source.mysql_source.properties')
    def test_fetch(self, mock_property, mock_sql_parser, mock_connection, mock_reader):
        mock_property.return_value = ""
        mock_sql_parser.return_value.parse_query.return_value = "select * from SAMPLE_TABLE"
        mock_reader.return_value.execute.return_value = DataFrame()
        source = MYSQLSource(self.input_source)
        data = source.fetch()
        assert data.size == 0

    @patch('ingen.data_source.mysql_source.pymysql')
    @patch('ingen.data_source.mysql_source.SqlQueryParser')
    @patch('ingen.data_source.mysql_source.properties')
    def test_fetch_validations(self, mock_property, mock_sql_parser, mock_connection):
        source = MYSQLSource(self.input_source)
        assert len(source.fetch_validations()) == 0


if __name__ == '__main__':
    unittest.main()
