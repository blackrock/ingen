#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

from ingen.writer.writer import InterfaceWriter

logger = logging.getLogger("writer")


class SplitFileWriter:

    def __init__(self, df, output_type, writer_props, params):
        self._df = df
        self._type = output_type
        self._props = writer_props
        self._params = params

    def get_filtered_results(self, column, value):
        return self._df.loc[self._df[column] == value]

    def write(self):
        for file in self._props:
            filtered_df = self.get_filtered_results(file['col'], file['value'])
            writer = InterfaceWriter(filtered_df.reset_index(drop=True), file.get('type'), file.get('props'),
                                     self._params)
            writer.write()
