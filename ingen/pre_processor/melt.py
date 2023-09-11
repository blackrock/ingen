#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

class Melt:
    def execute(self, config, sources_data, data):
        return self.melt_column_to_row(config, sources_data)

    def melt_column_to_row(self, config, sources_data):
        """
        convert columns to rows
        :param config:
        :param sources_data:
        include_keys: Column(s) to unpivot. If not specified, uses all columns that are not set as id_vars.
        key_column:   Name to use for the ‘variable’ column
        value_column:  Name to use for the ‘value’ column
        :return: updated dataframe

        """

        dataframe = sources_data[config['source'][0]]  # this operation will be performed only on one dataframe
        value_name = config.get('value_column')
        var_name = config.get('key_column')
        value_vars = config.get('include_keys')
        if len(value_vars) == 0:
            dataframe = dataframe.melt(value_name=value_name, var_name=var_name)
        else:
            dataframe = dataframe.melt(value_vars=value_vars, value_name=value_name, var_name=var_name)
        return dataframe
