#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

def groupby(config, data):
    return data.groupby(config['cols'])


def agg(config, data):
    return data.agg(config['operation'], config['col'])


aggregator_map = {
    'groupby': groupby,
    'agg': agg

}


def get_aggregator(aggregator_type):
    return aggregator_map.get(aggregator_type)

def add_aggregator(aggregator_type, aggregator):
    return aggregator_map.update( {aggregator_type: aggregator} )