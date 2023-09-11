#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

from ingen.writer.json_writer.convertors.df_to_multiple_json_convertor import DFToMultipleJsonConvertor
from ingen.writer.json_writer.convertors.df_to_single_json_convertor import DFToSingleJsonConvertor

logger = logging.getLogger("json_convertor_factory")


def get_json_convertor(convertor_name):
    if convertor_name == 'single':
        return DFToSingleJsonConvertor()
    elif convertor_name == 'multiple':
        return DFToMultipleJsonConvertor()
    else:
        logger.error(f'Unknown convertor name passed "{convertor_name}"')
