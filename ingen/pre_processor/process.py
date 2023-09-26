#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

class Process:
    """
    A Process represents a process to be applied on the dataframe(s). All process must implement
    a method called execute, which is responsible for processing and returning data and returning a processed dataframe
    """

    def execute(self, config, sources_data, data):
        """
        Method responsible for executing the processing step on data
        :param config: configuration to use for merging the data
        :param sources_data: array of data from all sources
        :param data: pre-processed data till now
        :return: A Pandas DataFrame with the result of the process
        """
        pass
