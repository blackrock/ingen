import logging
import pandas as pd

log = logging.getLogger()

def pivot_to_dynamic_columns(dataframe, config):
    """
    Converts a dataframe with dynamic attributes to a wide format by pivoting based on
    a specified column and value. It replaces NaN values with empty strings and retains
    rows without dynamic attributes.

    The function automatically uses all columns except the pivot and value columns as
    the index for the pivoting operation. Static rows (those without dynamic attributes)
    are preserved in the output.

    :param dataframe: The input DataFrame containing dynamic attributes.
    :param config: A dictionary containing 'pivot_col' (column to pivot) and
                   'value_col' (column containing values to fill).
    :return: A pivoted DataFrame with dynamic columns, NaN replaced with empty strings.
    """
    pivot_col = config.get('pivot_col')
    if pivot_col not in dataframe.columns:
        raise KeyError(f"Column {pivot_col} not found.")

    value_col = config.get('value_col')
    if value_col not in dataframe.columns:
        raise KeyError(f"Column {value_col} not found.")

    dataframe = dataframe.applymap(lambda x: '' if pd.isna(x) or (isinstance(x, str) and x.strip() == '') else x)
    dynamic_rows = dataframe[dataframe[pivot_col] != '']
    static_rows = dataframe[dataframe[pivot_col] == '']

    index_cols = [col for col in dynamic_rows.columns if col not in [pivot_col, value_col]]
    df_pivot = dynamic_rows.pivot_table(index=index_cols, columns=pivot_col, values=value_col, aggfunc='first').reset_index()

    df_pivot.columns.name = None
    df_pivot = df_pivot.rename_axis(None, axis=1)

    if not static_rows.empty:
        static_rows = static_rows.drop([pivot_col, value_col], axis=1).drop_duplicates()
        df_pivot = pd.merge(df_pivot, static_rows, on=index_cols, how='outer')
    return df_pivot