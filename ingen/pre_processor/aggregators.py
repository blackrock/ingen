#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

def groupby(config, data):
    return data.groupby(config['cols'])


def agg(config, data):
    return data.agg(config['operation'], config['col'])


def get_aggregator(formatter_type):
    if formatter_type == 'groupby':
        return groupby
    elif formatter_type == 'agg':
        return agg
