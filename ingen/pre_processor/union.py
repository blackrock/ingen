#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pandas as pd


class Union:
    def execute(self, config, sources_data, data):
        return self.concat(config, sources_data)

    def concat(self, config, sources_data):
        dataframes = [sources_data[source] for source in config['source']]
        if config.get('direction') is None or config.get('direction') == 0:
            axis = 0  # represents rows
        elif config.get('direction') == 1:
            axis = config.get('direction')  # axis 1 represents columns
        else:
            raise KeyError('direction(or axis) keyword can accept either 0 or 1')
        return pd.concat(dataframes, axis=axis)
