#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

import pandas as pd

log = logging.getLogger()


class SnowflakeReader:
    def __init__(self, connection):
        self._connection = connection

    def execute(self, sql):
        log.info(f"Running query: {sql}")
        try:
            with self._connection.cursor() as cursor:
                cursor.execute(sql)
                columns = [col[0] for col in cursor.description]
                dataframe = pd.DataFrame.from_records(cursor.fetchall(), columns=columns)
            log.info(f"TOTAL RECORDS IN DATAFRAME FROM SNOWFLAKE: {len(dataframe)}")
            return dataframe
        finally:
            self._connection.close()
