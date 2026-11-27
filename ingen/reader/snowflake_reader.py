#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

import pandas as pd

log = logging.getLogger()

DEFAULT_BATCH_SIZE = 100000


class SnowflakeReader:
    def __init__(self, connection, batch_size=DEFAULT_BATCH_SIZE):
        self._connection = connection
        self._batch_size = batch_size

    def execute(self, sql):
        log.debug(f"Running query: {sql}")
        try:
            with self._connection.cursor() as cursor:
                cursor.execute(sql)
                columns = [col[0] for col in cursor.description]
                # Rows are fetched and converted to DataFrames batch by batch, so the full result set is never held
                # in memory as Python row tuples (several times larger than the equivalent DataFrame).
                batches = [pd.DataFrame.from_records(rows, columns=columns)
                           for rows in iter(lambda: cursor.fetchmany(self._batch_size), [])]
            dataframe = pd.concat(batches, ignore_index=True) if batches else pd.DataFrame(columns=columns)
            log.info(f"TOTAL RECORDS IN DATAFRAME FROM SNOWFLAKE: {len(dataframe)}")
            return dataframe
        finally:
            self._connection.close()
