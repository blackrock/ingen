#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

def groupby(config, data):
    """
    groups data by configured column

    :param config : columns for grouping
    :param data : data to be aggregated
    """
    return data.groupby(config['cols'])


def agg(config, data):
    """
    aggregates passed data as per configuration

    :param config : configuration for aggregator
    :param data : data to be aggregated
    """
    return data.agg(config['operation'], config['col'])


aggregator_map = {
    'groupby': groupby,
    'agg': agg

}


def get_aggregator(aggregator_type):
    """
    gets an aggregator, returns aggregator function

    :param aggregator_type : name/type of the aggregator
    """
    return aggregator_map.get(aggregator_type)

def add_aggregator(aggregator_type, aggregator):
    """
    adds a new aggregator

    :param aggregator_type : name/type of the aggregator
    :param aggregator : aggregator function
    """
    return aggregator_map.update( {aggregator_type: aggregator} )