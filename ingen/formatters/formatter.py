#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from ingen.formatters.common_formatters import *

log = logging.getLogger()


class Formatter:
    def __init__(self, df, columns, params):
        self._df = df
        self._columns = columns
        self._id_name_map = self.map_column_id_name()
        self._param = params

    def map_column_id_name(self):
        id_name_map = {}
        for column in self._columns:
            id_name_map[column['src_col_name']] = column['dest_col_name'] if 'dest_col_name' in column else column[
                'src_col_name']
        return id_name_map

    def apply_format(self):
        for column in self._columns:
            for formatter in column.get('formatters', []):
                formatter_func = get_formatter_from_type(formatter['type'])
                col_name = column.get('src_col_name')
                if formatter_func is None:
                    raise ValueError(f"Invalid formatter type: {formatter.get('type')} "
                                     f"on column {col_name}")
                log.info(f"Formatting column {col_name} using {formatter.get('type')} formatter")
                start = time.time()
                self._df = formatter_func(self._df, col_name, formatter.get('format'), self._param)
                end = time.time()
                log.info(f"Finished '{formatter.get('type')}' formatter on column {col_name} "
                         f"in {end - start:.2f} seconds")

        column_names = [col['src_col_name'] for col in self._columns]
        self._df = column_filter(self._df, column_names)
        self._df = name_formatter(self._df, self._id_name_map)
        return self._df
