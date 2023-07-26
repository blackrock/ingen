import pandas as pd

DEFAULT_CONVERTOR = "pandas_normalize"


def pandas_normalize(responses, data_node, data_key, meta=None):
    """
    Default conversion method to convert json responses to DataFrame
    using pandas json_normalize method. This function should suffice
    all major use cases.
    """
    result = []
    if len(responses) == 0:
        return pd.DataFrame()
    elif type(responses[0]) == list:
        for response in responses:
            result.extend(response)
        return pandas_normalize(result, data_node, data_key, meta)
    elif type(responses[0]) == str:
        return pd.DataFrame(responses)
    else:
        result = responses
    df = pd.json_normalize(result, record_path=data_node, meta=meta)

    return _filtered_df(df, data_key, meta)


def _filtered_df(df, data_key, meta):
    if data_key is None and meta is None:
        return df

    cols = []
    if data_key:
        for key in data_key:
            cols.append(key)

    if meta:
        for key in meta:
            if type(key) == list:
                cols.append(".".join(key))
            else:
                cols.append(key)

    return df[cols]


def response_to_list(responses, data_node, data_key, meta):
    if len(responses) > 0:
        response_values = [response.values() for response in responses]
        result = []
        for values in response_values:
            result.extend(values)
        return pandas_normalize(result, data_node, data_key, meta)
    return pd.DataFrame()


CONVERTORS = {
    "pandas_normalize": pandas_normalize,
    "response_to_list": response_to_list
}


def get_json_to_df_convertor(func_name=DEFAULT_CONVERTOR):
    return CONVERTORS.get(func_name)
