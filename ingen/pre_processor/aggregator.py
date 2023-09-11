#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from ingen.pre_processor.aggregators import *
from ingen.pre_processor.process import Process


class Aggregator(Process):

    def execute(self, config, sources_data, data):
        return self.aggregate(config, data)

    def aggregate(self, config, data):
        if data.empty:
            return data

        operations = list(config.keys())
        operations.remove('type')
        for operation in operations:
            operator = get_aggregator(operation)
            data = operator(config[operation], data)
        return data.reset_index()
