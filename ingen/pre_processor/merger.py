#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pandas as pd

from ingen.pre_processor.process import Process


class Merger(Process):
    DEFAULT_MERGE_TYPE = 'inner'

    def execute(self, config, sources_data, data):
        """
        method responsible for calling the appropriate function to execute the process
        :param config: configuration to use for merge
        :param sources_data: dictionary of data fetched from sources
        :param data: pre-processed data till now
        :return: A Pandas dataframe which is the result of the merge process
        """
        left_dataframe = data
        right_dataframe = sources_data.get(config.get('source'))
        merge_type = config.get('merge_type', self.DEFAULT_MERGE_TYPE)
        left_key = config.get('left_key')
        right_key = config.get('right_key')

        if left_key is not None and not pd.Series(left_key).isin(left_dataframe.columns).all():
            raise KeyError(f"Column '{left_key}' not present in left dataframe")

        if right_key is not None and not pd.Series(right_key).isin(right_dataframe.columns).all():
            raise KeyError(f"Column '{right_key}' not present in right dataframe")

        return self.merge(left_dataframe, right_dataframe, left_key, right_key, merge_type)

    def merge(self, left, right, left_key, right_key, how):
        """
        Merge two dataframes
        :param left: left dataframe
        :param right: right dataframe
        :param left_key: column name to join on in left dataframe
        :param right_key: column name to join on in right dataframe
        :param how: type of merge to be performed
        :return: merged dataframe
        """
        return pd.merge(left, right, left_on=left_key, right_on=right_key, how=how)
