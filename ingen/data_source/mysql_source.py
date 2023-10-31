#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

import pymysql
from ingen.data_source.source import DataSource
from ingen.reader.mysql_reader import MYSQLReader
from ingen.utils.properties import properties
from ingen.utils.sql_query_parser import SqlQueryParser
from ingen.utils.timer import log_time

log = logging.getLogger()


class MYSQLSource(DataSource):
    """
    This class represents mysql database source
    """

    _connection = None

    def __init__(self, source, params_map=None):
        """
        Loads a MYSQLSource
        :param source: Map which contains source data such as id, query, etc.
        :param params_map: Map which contains runtime parameters such as query_params, run_date
        """
        super().__init__(source['id'])
        self._src_data_checks = source.get('src_data_checks', [])
        self._host = properties.get_property('datasource.mysql.host')
        self._user = properties.get_property('datasource.mysql.user')
        self._password = properties.get_property('datasource.mysql.password')
        self._database = source.get('database')
        self._query = SqlQueryParser().parse_query(source['query'], params_map, source.get('temp_table_params'))
        if self._connection is None:
            self._connection = pymysql.connect(host=self._host,
                                                          user=self._user,
                                                          password=self._password,
                                                          database=self._database)
        else:
            raise Exception('You cannot create another MySQL connection')

    def fetch(self):
        """
        Executes the SQL query
        :return: A DataFrame created using the result of the query
        """
        reader = MYSQLReader(self._connection)
        return self.fetch_data(reader)

    @log_time
    def fetch_data(self, reader):
        """
        returns a DataFrame of data fetched from MySQLSource.
        """
        return reader.execute(self._query)

    def fetch_validations(self):
        """
        Method to fetch validations from the source
        :return: list of dictionaries containing mentioned validations on all columns
        """
        return self._src_data_checks
