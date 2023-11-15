#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging
import os
from datetime import date

from ingen.utils.interpolators.Interpolator import Interpolator

ENVIRONMENT_VAR_PATTERN = "$$"


class PathParser:
    """
    PathParser is a utility class that provides methods to parse file paths and replace
    the dynamic fields in it with appropriate values. A replaceable item can be one of the following:
        1. date - $date(<FORMAT>) - it will be replaced by the date provided in the constructor in the given format
    """

    def __init__(self, run_date=date.today(), interpolator=Interpolator()):
        self.run_date = run_date
        self.interpolator = interpolator
        self.item_name_method_map = {
            'date': self.get_formatted_run_date
        }

    def parse(self, path):
        """
        Replaces bfm tokens and dates in the file paths
        :param path: file path string. e.g, "$token(FTP_DIR)/some/path/file_name_$date(%d%m%Y).csv"
        :return: path with tokens and date values. e.g, "u1/ftp/some/path/file_name_12092020.csv"
        """
        path = self.parse_env_variable(path)
        return self.interpolator.interpolate(path, self.item_name_method_map)

    def parse_env_variable(self, path):
        if path.startswith(ENVIRONMENT_VAR_PATTERN):
            environment_var = path[2:]
            path = os.getenv(environment_var)
            if path is None:
                logging.error(f'Could not parse file path. Environment variable "{environment_var}" is not set.')
                raise ValueError
        return path

    def get_formatted_run_date(self, date_format, params=None):
        return self.run_date.strftime(date_format)
