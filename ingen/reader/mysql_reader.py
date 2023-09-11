#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

import pandas as pd

log = logging.getLogger()


class MYSQLReader:
    def __init__(self, connection):
        self._connection = connection

    def execute(self, sql):
        log.info(f"Running query: {sql}")
        try:
            dataframe = pd.read_sql(sql, self._connection)
            log.info(f"TOTAL RECORDS IN DATAFRAME FROM MYSQL: {len(dataframe)}")
            return dataframe
        finally:
            self._connection.close()
