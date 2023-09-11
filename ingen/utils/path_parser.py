#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging
from datetime import date

from ingen.utils.interpolators.Interpolator import Interpolator
from ingen.utils.parse_utils import ENVIRONMENT_VAR_PATTERN
from ingen.utils.parse_utils import var_starts_with, get_environment_value


class PathParser:
    """
    PathParser is a utility class that provides methods to parse file paths and replace
    the dynamic fields in it with appropriate values. A replaceable item can be one of the following:
        1. bfm_token - $token(<TOKEN>) - it will be replaced by the value of 'TOKEN' as written in files.date file
        2. date - $date(<FORMAT>) - it will be replaced by the date provided in the constructor in the given format
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
        if var_starts_with(path, ENVIRONMENT_VAR_PATTERN):
            environment_var = path[2:]
            path = get_environment_value(environment_var)
            if path is None:
                logging.error(f'Could not parse file path. Environment variable "{environment_var}" is not set.')
                raise ValueError
        return path

    def get_formatted_run_date(self, date_format, params=None):
        return self.run_date.strftime(date_format)
