#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging
from datetime import date

import numpy as np

from ingen.reader.file_reader import ReaderFactory
from ingen.utils.path_parser import PathParser


class SqlQueryParser:
    """
    Helper class to parse dynamic SQL queries, and replace the dynamic parts of the queries with their actual values
    provided in either command line parameters or via a file.
    """

    @classmethod
    def parse_query(cls, query, cmd_line_params, temp_table_params_config=None):
        """
        Parses the SQL query string and returns the actual query.
        :param query                        SQL query
        :param cmd_line_params              parameters passed from the command line, query_params + run_date
        :param temp_table_params_config     parameters to create temp table from file or api
        :return: SQL query with dynamic parameters replaced by their values from temp_table_params
        """
        if cmd_line_params is not None:
            cls.run_date = cmd_line_params.get('run_date', date.today())
            cls.cmd_line_query_params = cmd_line_params.get('query_params')
        else:
            cls.run_date = date.today()
            cls.cmd_line_query_params = None
        try:
            query_param_mapping = {}
            if cls.cmd_line_query_params is not None:
                query_param_mapping.update(cls.cmd_line_query_params)
            if temp_table_params_config is not None:
                temp_table_query = cls.create_temp_table(temp_table_params_config)
                query = temp_table_query + query
            return query.format(**query_param_mapping)

        except KeyError as error:
            logging.error('Error parsing sql query. Required query params not provided')
            raise error

    @classmethod
    def read_data(cls, temp_table_config):
        """
            Read the file based on file parmas
            :param  temp_table_config    describes the config for files to be read
            :return: file data as dataframe
            """
        reader = ReaderFactory.get_reader(temp_table_config)
        temp_table_config['file_path'] = PathParser(cls.run_date).parse(temp_table_config['file_path'])
        file_data = reader.read(temp_table_config)
        return file_data

    @classmethod
    def fill_empty_values(cls, key, col_type):
        if 'default_val_if_empty' in key:
            default_val = key['default_val_if_empty']
        elif (col_type == 'char' or col_type == 'nchar' or col_type == 'varchar' or key[
            'type'] == 'nvarchar'):
            default_val = ''
        elif (col_type == 'int' or col_type == 'smallint' or col_type == 'bigint' or key[
            'type'] == 'tinyint'):
            default_val = 0
        return default_val

    @classmethod
    def insert_values(cls, temp_table_config):
        """
        Parse the temp table config, read the config from file , insert the data from file to temp table and return a
        list of queries
        :param  temp_table_config    describes the config to create temp table
        :return: list of temp table queries
        """
        temp_table_name = temp_table_config['temp_table_name']
        temp_table_cols = temp_table_config['temp_table_cols']
        col_config = ''
        col_list = ''
        file_cols = []
        default_values = {}
        for key in temp_table_cols:
            col_name = key['name']
            col_type = key['type']
            file_col = key['file_col']
            col_size = f"({key.get('size')})" if 'size' in key else ''
            separtaor = '' if key == temp_table_cols[-1] else ','
            col_config += col_name + f" " + col_type + col_size + separtaor
            col_list += col_name + separtaor
            file_cols.append(file_col)
            default_val = cls.fill_empty_values(key, col_type)
            default_values.update({f"{file_col}": default_val})

        # create temptable query.
        temp_table_queries = [f"create table #{temp_table_name} ({col_config})"]
        insert_string = f"INSERT INTO #{temp_table_name} ({col_list}) VALUES"
        # read the data via file reader
        file_data = cls.read_data(temp_table_config)
        for key in file_cols:
            if key not in file_data.columns:
                raise KeyError(f"Column '{key}' not found in input file or input file does not have header")
        file_df = file_data[file_cols].replace(np.nan, default_values)

        if len(file_df) > 0:
            for row in zip(*file_df.to_dict("list").values()):
                df_col_val = F" {row}"
                if len(temp_table_cols) == 1:
                    col_val = df_col_val.replace(',', '')
                else:
                    col_val = df_col_val
                temp_table_queries.append(f"{insert_string + col_val}")
        return temp_table_queries

    @classmethod
    def create_temp_table(cls, temp_table_params):
        """
         Parse the temp table params, return a query string
         :param  temp_table_params    describes the config to create temp table
         :return: string of temp table queries
         """
        temp_table_query = []
        for temp_table_config in temp_table_params:
            if temp_table_config['type'] == 'file':
                temp_table_query.extend(cls.insert_values(temp_table_config))

        return ';'.join(temp_table_query) + ';'
