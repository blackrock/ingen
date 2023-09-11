#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from ingen.writer.json_util import process_dataframe_columns_schema


class OldJSONWriter:
    """
        Class consisting methods to convert and write JSON file to path provided in config
    """

    def __init__(self, df, output_type, writer_props):
        """
        Initialize json writer properties
        :param df: input dataframe
        :param output_type: expected output format
        :param writer_props: configurable properties for data processing
        """
        self._df = df
        self._type = output_type
        self._props = writer_props

    def write(self):
        """
            Method to write JSON file to path provided in config,
            with given orientation and indentation on the JSON output file
        """
        path = self._props.get("path", None)
        json_config = self._props.get("config")
        indent = json_config.get("indent")
        orient = json_config.get("orient")
        column_details = json_config.get("column_details")
        json_object = process_dataframe_columns_schema(df=self._df, column_details=column_details)
        json_object.to_json(path_or_buf=path, orient=orient, indent=indent)
