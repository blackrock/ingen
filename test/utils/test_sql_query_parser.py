#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import datetime
import os
import unittest
from unittest.mock import patch, Mock

import pandas as pd

from ingen.utils.sql_query_parser import SqlQueryParser


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.query_parser = SqlQueryParser()

    def test_parse_query_with_no_params(self):
        query = 'select top 10 * from positions'
        query_params = None
        self.assertEqual(query, self.query_parser.parse_query(query, query_params))

    def test_parse_query_with_query_params(self):
        query = 'select top 10 * from {table_name}'
        query_params = {'query_params': {'table_name': 'positions'}}
        expected_query = 'select top 10 * from positions'
        self.assertEqual(expected_query, self.query_parser.parse_query(query, query_params))

    @patch('ingen.utils.sql_query_parser.logging')
    def test_parse_query_when_params_not_provided(self, mock_logging):
        query = 'select top 10 * from {table_name}'
        no_query_params = None
        expected_error_msg = 'Error parsing sql query. Required query params not provided'
        with self.assertRaisesRegex(KeyError, "'table_name'"):
            self.query_parser.parse_query(query, no_query_params)
        mock_logging.error.assert_called_with(expected_error_msg)

    @patch('ingen.utils.sql_query_parser.ReaderFactory')
    def test_parse_query_with_numbers_in_file(self, mock_reader_factory):
        data = {'ALIAS_CODE': (5005, 1234)}
        mock_file_data = pd.DataFrame(data)
        mock_reader = Mock()
        mock_reader_factory.get_reader.return_value = mock_reader
        mock_reader.read.return_value = mock_file_data

        cmd_line_query_params = None
        query = "select * from cusip_table, #temp_table temp_table where purpose = temp_table.alias_code"
        expected_query = "create table #temp_table (alias_code int);" \
                         "INSERT INTO #temp_table (alias_code) VALUES (5005);" \
                         "INSERT INTO #temp_table (alias_code) VALUES (1234);" \
                         "select * from cusip_table, #temp_table temp_table where purpose = " \
                         "temp_table.alias_code"

        temp_table_param = [{'id': 'file1', 'type': 'file', 'file_type': 'delimited_file', 'delimiter': ',',
                             'file_path': 'test/path', 'skip_trailer_size': 0,
                             'skip_header_size': 1, 'temp_table_name': 'temp_table',
                             'temp_table_cols': [{'name': 'alias_code', 'type': "int", "file_col": "ALIAS_CODE"}]}]

        actual_query = self.query_parser.parse_query(query, cmd_line_query_params, temp_table_param)
        self.assertEqual(expected_query, actual_query)

    def test_parse_query_with_multiple_columns_in_file(self):
        script_dir = os.path.dirname(__file__)
        source_file_path = '../input/test1.csv'

        cmd_line_query_params = None

        query = "select name as NAME from students, #temp_table temp_table" \
                "where subject = 'English' and subject.id = temp_table.id"
        expected_query = "create table #temp_table (id varchar(50),course_name varchar(50));INSERT INTO #temp_table ("\
                         "id,course_name) VALUES (1, 'Literature');" \
                         "INSERT INTO #temp_table (id,course_name) VALUES (2, 'Political Science');" \
                         "select name as NAME from students, #temp_table temp_table" \
                         "where subject = 'English' and subject.id = temp_table.id"

        temp_table_param = [{'id': 'file1', 'type': 'file', 'file_type': 'delimited_file', 'delimiter': ',',
                             'file_path': os.path.join(script_dir, source_file_path), 'skip_trailer_size': 0,
                             'temp_table_name': 'temp_table',
                             'temp_table_cols': [
                                 {'name': 'id', 'type': "varchar", 'size': 50, "file_col": "ID"},
                                 {'name': 'course_name', 'type': "varchar", 'size': 50, "file_col": "COURSE_NAME"}]}]

        actual_query = self.query_parser.parse_query(query, cmd_line_query_params, temp_table_param)
        self.assertEqual(expected_query, actual_query)

    @patch('ingen.utils.sql_query_parser.ReaderFactory')
    def test_parse_query_with_dynamic_file_path(self, mock_reader_factory):
        date_format = "%d%m%Y"
        date = datetime.date.today()
        source_file_path = f'../input/test_$date({date_format}).csv'
        expected_path = f'../input/test_{date.strftime(date_format)}.csv'

        data = {'CUSIP': ('BACH890LK', 'BHNK98J80')}
        mock_file_data = pd.DataFrame(data)
        mock_reader = Mock()
        mock_reader_factory.get_reader.return_value = mock_reader
        mock_reader.read.return_value = mock_file_data

        cmd_line_query_params = None
        query = "select * from cusip_table, #temp_table temp_table where bfm_cusip = temp_table.bcusip"
        expected_query = "create table #temp_table (bcusip varchar(50));" \
                         "INSERT INTO #temp_table (bcusip) VALUES ('BACH890LK');" \
                         "INSERT INTO #temp_table (bcusip) VALUES ('BHNK98J80');" \
                         "select * from cusip_table, #temp_table temp_table where bfm_cusip = " \
                         "temp_table.bcusip"

        temp_table_param = [{'id': 'file1', 'type': 'file', 'file_type': 'delimited_file', 'delimiter': ',',
                             'file_path': source_file_path, 'skip_trailer_size': 0,
                             'skip_header_size': 1, 'temp_table_name': 'temp_table',
                             'temp_table_cols': [
                                 {'name': 'bcusip', 'type': "varchar", 'size': 50, "file_col": "CUSIP"}]}]

        expected_temp_table_param = {'id': 'file1', 'type': 'file', 'file_type': 'delimited_file',
                                     'delimiter': ',',
                                     'file_path': expected_path, 'skip_trailer_size': 0,
                                     'skip_header_size': 1,
                                     'temp_table_name': 'temp_table',
                                     'temp_table_cols': [
                                         {'name': 'bcusip', 'type': "varchar", 'size': 50, "file_col": "CUSIP"}]}

        actual_query = self.query_parser.parse_query(query, cmd_line_query_params, temp_table_param)
        mock_reader.read.assert_called_with(expected_temp_table_param)
        self.assertEqual(expected_query, actual_query)

    @patch('ingen.utils.sql_query_parser.ReaderFactory')
    def test_parse_query_with_dynamic_file_path_and_new_date(self, mock_reader_factory):
        date_format = "%d%m%Y"
        date = datetime.datetime(2020, 9, 12)  # past date
        source_file_path = f'../input/test_$date({date_format}).csv'
        expected_path = f'../input/test_{date.strftime(date_format)}.csv'

        data = {'CUSIP': ('BACH890LK', 'BHNK98J80')}
        mock_file_data = pd.DataFrame(data)
        mock_reader = Mock()
        mock_reader_factory.get_reader.return_value = mock_reader
        mock_reader.read.return_value = mock_file_data

        cmd_line_query_params = {'run_date': date}
        query = "select * from cusip_table, #temp_table temp_table where bfm_cusip = temp_table.bcusip"
        expected_query = "create table #temp_table (bcusip varchar(50));" \
                         "INSERT INTO #temp_table (bcusip) VALUES ('BACH890LK');" \
                         "INSERT INTO #temp_table (bcusip) VALUES ('BHNK98J80');" \
                         "select * from cusip_table, #temp_table temp_table " \
                         "where bfm_cusip = temp_table.bcusip"

        temp_table_params = [{'id': 'file1', 'type': 'file', 'file_type': 'delimited_file', 'delimiter': ',',
                              'file_path': source_file_path, 'skip_trailer_size': 0,
                              'skip_header_size': 1, 'temp_table_name': 'temp_table',
                              'temp_table_cols': [
                                  {'name': 'bcusip', 'type': "varchar", 'size': 50, "file_col": "CUSIP"}]}]

        expected_temp_table_params = {'id': 'file1', 'type': 'file', 'file_type': 'delimited_file', 'delimiter': ',',
                                      'file_path': expected_path, 'skip_trailer_size': 0,
                                      'skip_header_size': 1, 'temp_table_name': 'temp_table',
                                      'temp_table_cols': [
                                          {'name': 'bcusip', 'type': "varchar", 'size': 50, "file_col": "CUSIP"}]}

        actual_query = self.query_parser.parse_query(query, cmd_line_query_params, temp_table_params)
        mock_reader.read.assert_called_with(expected_temp_table_params)
        self.assertEqual(expected_query, actual_query)

    def test_parse_query_with_only_temp_table_query_params(self):
        script_dir = os.path.dirname(__file__)
        source_file_path = '../input/test1.csv'
        cmd_line_query_params = None

        query = "select DATA, COURSE_NAME, ID FROM test_table"
        expected_query = "create table #temp_id (ID varchar(50));INSERT INTO #temp_id (ID) VALUES (1);INSERT INTO #temp_id (ID) VALUES (2);select DATA, COURSE_NAME, ID FROM "'test_table'""

        temp_table_params = [{'id': 'file1', 'type': 'file', 'file_type': 'delimited_file', 'delimiter': ',',
                              'file_path': os.path.join(script_dir, source_file_path),
                              'temp_table_name': 'temp_id',
                              'temp_table_cols': [
                                  {'name': 'ID', 'type': "varchar", 'size': 50, "file_col": "ID",
                                   "default_val_if_empty": "temp_string"}]}]
        actual_query = self.query_parser.parse_query(query, cmd_line_query_params, temp_table_params)
        print(actual_query)
        self.assertEqual(expected_query, actual_query)

    def test_parse_query_with_cmd_line_params_and_temp_table_query_params(self):
        script_dir = os.path.dirname(__file__)
        source_file_path = '../input/test1.csv'
        cmd_line_query_params = {'query_params': {'ID': '1'}}

        query = "select DATA, COURSE_NAME, ID FROM test_table"
        expected_query = "create table #temp_id (ID varchar(50));INSERT INTO #temp_id (ID) VALUES (1);INSERT INTO #temp_id (ID) VALUES (2);select DATA, COURSE_NAME, ID FROM "'test_table'""

        temp_table_params = [{'id': 'file1', 'type': 'file', 'file_type': 'delimited_file', 'delimiter': ',',
                              'file_path': os.path.join(script_dir, source_file_path),
                              'temp_table_name': 'temp_id',
                              'temp_table_cols': [
                                  {'name': 'ID', 'type': "varchar", 'size': 50, "file_col": "ID",
                                   "default_val_if_empty": "temp_string"}]}]

        actual_query = self.query_parser.parse_query(query, cmd_line_query_params, temp_table_params)
        self.assertEqual(expected_query, actual_query)

    @patch('ingen.utils.sql_query_parser.ReaderFactory')
    def test_parse_query_with_multiple_temp_table_params(self, mock_reader_factory):
        query = "select distinct t.cusip from (select cusip from #temp1 union select cusip from #temp2) t"

        expected_query = "create table #temp1 (cusip varchar(9));" \
                         "insert into #temp1 (cusip) values ('abcd');" \
                         "insert into #temp1 (cusip) values ('abce');" \
                         "create table #temp2 (cusip varchar(9));" \
                         "insert into #temp2 (cusip) values ('abcd');" \
                         "insert into #temp2 (cusip) values ('abce');" \
                         "select distinct t.cusip from (select cusip from #temp1 union select cusip from #temp2) t"

        data = {'cusip': ('abcd', 'abce')}
        mock_file_data = pd.DataFrame(data)
        mock_reader = Mock()
        mock_reader_factory.get_reader.return_value = mock_reader
        mock_reader.read.return_value = mock_file_data

        temp_table_params = [{'id': 'file1', 'type': 'file', 'file_type': 'delimited_file', 'delimiter': ',',
                              'file_path': 'test/path', 'temp_table_name': 'temp1',
                              'temp_table_cols':
                                  [{'name': 'cusip', 'type': "varchar", 'size': 9, "file_col": "cusip"}]
                              },
                             {'id': 'file2', 'type': 'file', 'file_type': 'delimited_file', 'delimiter': ',',
                              'file_path': 'test/path/2', 'temp_table_name': 'temp2',
                              'temp_table_cols':
                                  [{'name': 'cusip', 'type': "varchar", 'size': 9, "file_col": "cusip"}]
                              }]

        actual_query = self.query_parser.parse_query(query, None, temp_table_params)
        self.assertEqual(expected_query.lower(), actual_query.lower())


if __name__ == '__main__':
    unittest.main()
