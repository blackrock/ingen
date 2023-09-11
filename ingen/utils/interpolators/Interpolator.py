#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import re

from ingen.utils.interpolators.common_interpolators import COMMON_INTERPOLATORS


class Interpolator:
    def __init__(self, params=None):
        self.interpolator_function_map = None
        self.pattern = r"\$.*?\(.*?\)"
        self.item_name_pattern = r"\$(.*?)\(.*"
        self.item_args_pattern = r".*\((.*)\).*"
        self.params = params

    def interpolate(self, str_val, interpolator_function_map=None):
        """
        Accepts a string with dynamic tokens expressed as $function_name(function_args) and returns a string with
        the dynamic token replaced by their values. If 'function_name' is not found in the 'interpolator_function_map'
        the string is returned as is.
        :param interpolator_function_map: a map of function names and the actual function objects
        :param str_val: a string containing dynamic tokens
        :return: string with the dynamic tokens replaced by their values
        """
        if interpolator_function_map is None:
            interpolator_function_map = {}
        self.interpolator_function_map = {}
        self.interpolator_function_map.update(COMMON_INTERPOLATORS)
        self.interpolator_function_map.update(interpolator_function_map)
        return re.sub(self.pattern, self.parse_pattern, str_val)

    def parse_pattern(self, match):
        item_name_pattern = r"\$(.*?)\(.*"
        item_args_pattern = r".*\((.*)\).*"
        replaceable_item = match.group()
        item_name_match = re.match(item_name_pattern, replaceable_item)
        item_args_match = re.match(item_args_pattern, replaceable_item)

        item_name = item_name_match.groups()[0]
        item_args_list = item_args_match.groups()[0].split(",")

        item_method = self.interpolator_function_map.get(item_name)

        if item_method is not None:
            return item_method(*item_args_list, self.params)

        else:
            raise KeyError(f"No interpolator function found for '{item_name}'")
