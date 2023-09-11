#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import numpy as np

from ingen.pre_processor.process import Process


class Filter(Process):

    def execute(self, config, sources_data, data):

        # trim str values in dataframe for string comparison
        data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        cols = config.get('cols')
        operator = config.get('operator')

        return self.filter_by_column(data, cols, operator)

    def filter_by_column(self, data, cols, operator):

        if data.empty:
            return data

        filter_map = self.make_filter_map(cols)

        if operator == 'and':
            data = data[
                np.logical_and.reduce([
                    data[column].isin(target_values)
                    for column, target_values in filter_map.items()
                ])
            ]
        elif operator == 'or':
            data = data[
                np.logical_or.reduce([
                    data[col_name].isin(target_values)
                    for col_name, target_values in filter_map.items()
                ])
            ]

        return data

    def make_filter_map(self, cols):
        return dict((x.get('col'), x.get('val')) for x in cols)
