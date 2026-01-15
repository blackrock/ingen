import pandas as pd
from ingen.pre_processor.process import Process


class OuterJoin(Process): 
    """
    Pre-processor that performs a full outer join between two data sources.
    
    Usage in YAML:
        pre_processing:
        - type: outer_join
    source: «right_source_id> left_key: ‹left_column_name> right_key: <right_column_name>
    Columns from left source get '_x' suffix if duplicated.
    Columns from right source get '-y' suffix if duplicated.

    """

    def execute(self, config, sources_data, data):
        """
        Method responsible for calling the appropriate function to execute the outer join process.
        :param config: configuration to use for outer join
        :param sources_data: dictionary of data fetched from sources
        :param data: pre-processed data till now
        :return: A Pandas dataframe which is the result of the outer join process
        """
        left_dataframe = data
        right_dataframe = sources_data.get(config.get('source'))
        left_key = config.get('left_key')
        right_key = config.get('right_key')
        
        if left_key is not None and left_key not in left_dataframe.columns:
            raise KeyError(f"Column '{left_key}' not present in left dataframe")
        if right_key is not None and right_key not in right_dataframe.columns:
            raise KeyError(f"Column '{right_key}' not present in right dataframe")

        return self.outer_merge(left_dataframe, right_dataframe, left_key, right_key)

    def outer_merge(self, left_df, right_df, left_key, right_key):
        """Perform a full outer join on the two dataframes.

        :param: left_df: The left dataframe
        :param: right_df: The right dataframe
        :param: left_key: column name to join on in left dataframe
        :param: right_key: column name to join on in right dataframe
        :return: outer joined dataframe with NaN values converted to empty strings
        """
        result = pd.merge(left_df, right_df, how='outer', left_on=left_key, right_on=right_key)
        # Convert NaN to empty strings so column_condition formatters can compare with ""
        result = result.fillna('')
        return result
