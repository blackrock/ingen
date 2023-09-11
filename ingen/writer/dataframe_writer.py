#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from ingen.data_source.dataframe_store import store

'''A writer class that takes ID from the config file and writes a given dataframe directly to memory without creating 
intermediate interface files '''


class DataFrameWriter:

    def __init__(self, df, writer_props):
        self._df = df

        self.props = writer_props

    def write(self):
        df_id = self.props.get("id")
        store[df_id] = self._df
