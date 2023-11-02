#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from datetime import date


def process_dataframe_columns_schema(df, column_details):
    """
    Performs column schema processing on the dataframe as per the schema_config
    :param df:
    :param column_details:
    :return:
    """
    df_copy = df.copy()
    resultant_columns = column_details.get("resultant_columns", [])
    for details in column_details.get("schema"):
        field_name = details.get("field_name")
        field_type = details.get("field_type")
        field_attr = details.get("field_attr")
        field_action = details.get("field_action")
        if field_type == 'dict':
            df_copy[field_name] = df_copy[field_attr].to_dict('records')
            if field_action == 'groupby':
                field_action_column = details.get("field_action_column")
                field_agg_column = details.get("field_agg_column")
                df_copy = df_copy.groupby(field_action_column).agg({field_agg_column: lambda x: list(x)}).reset_index()
            if field_action == 'sum':
                field_action_column = details.get("field_action_column")
                field_agg_column = details.get("field_agg_column")
                field_total = details.get("field_total")
                df_copy[field_name] = df_copy[field_name]. \
                    apply(lambda x, agg_column=field_agg_column, action_column=field_action_column, total=field_total:
                          json_sum(x, agg_column, action_column, total))
        elif field_type == 'date':
            # TODO add handling for multiple date formats
            df_copy[field_name] = str(date.today())
        else:
            # just copy over the column from original dataframe
            df_copy[field_name] = df[field_name]
    return df_copy[resultant_columns]


def json_sum(obj, field=None, subfield=None, result=None):
    """
    Calculate the sum of a given collection in simple list,
    dict with array, dict with field and subfield as data
    :param obj: The collection object to be used for sum.
    :param field: Optional param, mandatory if passing a dict of format {'key': [1,2,3..]}
    :param subfield: Optional param, mandatory only if passing dict of format {'key':'value', 'key2': [{'key3':'value'}, {'key3':'value'}]}
    :param result: Optional param, mandatory if using dict mode.
    :return: float sum if using array mode, dict gets a column added which name is passed as result.
    """
    total = 0.0
    if field is None and subfield is None:
        total = sum(obj)
        return total
    elif subfield is None:
        total = sum(obj[field])
        obj[result] = total
        return obj
    else:
        for x in obj[field]:
            total += x[subfield]
        obj[result] = total
        return obj
