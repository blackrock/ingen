#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from ingen.writer.json_util import process_dataframe_columns_schema


class DFToSingleJsonConvertor:
    def convert(self, df, configs):
        indent = configs.get("indent")
        orient = configs.get("orient")
        column_details = configs.get("column_details")
        json_object = process_dataframe_columns_schema(df=df, column_details=column_details)
        return [json_object.to_json(orient=orient, indent=indent)]
