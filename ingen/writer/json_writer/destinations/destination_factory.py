#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

from ingen.writer.json_writer.destinations.api_destination import ApiDestination
from ingen.writer.json_writer.destinations.file_destination import FileDestination

logger = logging.getLogger("json_destination_factory")


def get_json_destination(destination_name, params=None):
    if destination_name == "file":
        return FileDestination()
    elif destination_name == "api":
        return ApiDestination(params)
    else:
        logger.error(f"Unknown destination name passed {destination_name}")
