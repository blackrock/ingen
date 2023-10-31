#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import calendar
import logging
import re
import time
import uuid
from datetime import datetime
from datetime import timedelta

import numpy as np
import pandas as pd

from ingen.formatters.utils import addition, subtract, divide, multiply
from ingen.lib.cryptor import Cryptor

pd.options.mode.chained_assignment = None
from ingen.utils.properties import Properties
from ingen.utils.utils import get_business_day

log = logging.getLogger()


def column_filter(dataframe, required_column_names):
    """
    Remove columns from dataframe that are not required
    :param dataframe: Dataframe
    :param required_column_names: List of required column names
    :return: Dataframe with only required columns in the desired order
    """
    all_columns = list(dataframe.columns)
    dataframe.drop(columns=[column for column in all_columns if column not in required_column_names])
    return dataframe.reindex(columns=required_column_names)


def name_formatter(dataframe, id_name_map):
    dataframe.columns = [id_name_map[col_id] for col_id in dataframe.columns]
    return dataframe


def encryption_formatter(dataframe, col_id, format_options, runtime_params):
    """
    Apply the encryption UDF on the selected column.
    :param dataframe: Input Data frame.
    :param col_id: The column to be encrypted
    :param format_options: Not required, but to be kept to not break the framework.
    :param runtime_params: Not required, but to be kept to not break the framework.
    :return:
    """
    cryptor = Cryptor()
    dataframe[col_id] = dataframe[col_id].apply(cryptor.encrypt)
    return dataframe


def decryption_formatter(dataframe, col_id, format_options, runtime_params):
    """
    Apply the decryption UDF on the selected column.
    :param dataframe: Input Data frame.
    :param col_id: The column to be decrypted
    :param format_options: Not required, but to be kept to not break the framework.
    :param runtime_params: Not required, but to be kept to not break the framework.
    :return:
    """
    cryptor = Cryptor()
    dataframe[col_id] = dataframe[col_id].apply(cryptor.decrypt)
    return dataframe


def date_formatter(dataframe, col_id, date_format, runtime_params):
    source_date_format = date_format['src']
    final_date_format = date_format['des']
    dataframe[col_id] = pd.to_datetime(dataframe[col_id], format=source_date_format)
    dataframe[col_id] = dataframe[col_id].map(lambda x: x.strftime(final_date_format) if pd.notnull(x) else '')
    return dataframe


def float_formatter(dataframe, col_id, float_format, runtime_params):
    dataframe[col_id] = dataframe[col_id].map(float_format.format)
    return dataframe


def constant_formatter(dataframe, col, const_string, runtime_params):
    dataframe[col] = const_string
    return dataframe


def constant_date_formatter(dataframe, col, format_options, runtime_params):
    try:
        date_offset, date_format, calendar_country = format_options
    except ValueError:
        error_msg = 'Missing required formatting attributes for constant date formatter. It should be a ' \
                    'list of date_offset, date_format and calendar_country. e.g., [0, "%Y%m%d", "US"]'
        log.error(error_msg)
        raise

    dataframe[col] = get_business_day(datetime.today() + timedelta(date_offset), 'next', calendar_country).strftime(
        date_format)
    return dataframe


def concat_formatter(dataframe, col_name, config, runtime_params):
    """
    Concatenates the provided columns and adds as a new column to the dataframe
    :param dataframe: original data frame
    :param col_name: name of the new column
    :param columns: list of names of columns to be concatenated
    :param runtime_params: command line arguments
    :return: dataframe with a new concatenated column
    """
    default_separator = ''
    separator = config.get('separator', default_separator)
    columns = config.get('columns')

    if any([column not in dataframe for column in columns]):
        log.error('Unknown column passed to concat formatter')
        raise ValueError

    dataframe[col_name] = dataframe[columns].astype(str).agg(separator.join, axis=1)
    return dataframe


def duplicate_column_formatter(dataframe, duplicate_col_name, original_col_name, runtime_params):
    """
    Adds a duplicate column with a new name
    :param dataframe: original dataframe
    :param duplicate_col_name: name to be given to the new column
    :param original_col_name: name of the column that is duplicated
    :param runtime_params: command line arguments
    :return: dataframe with a duplicate column
    """
    if original_col_name not in dataframe:
        log.error('Cannot create duplicate of a nonexistent column')
        raise KeyError

    dataframe[duplicate_col_name] = dataframe[original_col_name]
    return dataframe


def group_percentage_formatter(dataframe, col_name, format_options, runtime_params):
    """
    Adds a new column with the percentage of column A after grouping the dataframe by column B
    :param dataframe: original dataframe
    :param col_name: name of the new column
    :param format_options: name of column A and B in dictionary format.
    e.g., to calculate percentage of column A in column B, format_options = {'of': A, 'in': B}
    :param runtime_params: command line arguments
    :return: original dataframe with the new column added
    """
    of_col = format_options.get('of')
    in_col = format_options.get('in')

    column_names = list(dataframe.columns)
    if of_col not in column_names or in_col not in column_names:
        log.error('Unknown column names provided for calculating grouped percentage.')
        raise ValueError

    dataframe[col_name] = dataframe.groupby(in_col)[of_col].transform(lambda x: 100 * x / sum(x))
    return dataframe


def sum_value_formatter(dataframe, col_name, columns, runtime_params):
    """
        Adds a new column with the summation of column A and column B
        :param dataframe: original dataframe
        :param col_name: name of the new column
        :param columns: columns which are to be added
        :param runtime_params: command line arguments
        :return: original dataframe with the new column added
        """
    if any([column not in dataframe for column in columns]):
        log.error('Unknown column passed to concat formatter')
        raise ValueError
    dataframe[col_name] = dataframe[columns[0]] + dataframe[columns[1]]
    return dataframe


def date_diff_formatter(dataframe, col_name, format_options, runtime_params):
    """
    Calculates the number of days between two date columns and inserts the difference in a new column
    :param dataframe: original dataframe
    :param col_name: name of the new column
    :param format_options: list containing containing column names of from_date, to_date and date_format
    :param runtime_params: command line arguments, not required by this formatter
    :return: original dataframe with the new column added
    """

    from_date = format_options[0]
    to_date = format_options[1]
    date_format = format_options[2]
    if from_date not in dataframe or to_date not in dataframe:
        raise KeyError("Column does not exist in dataframe. Check column names in the date-diff formatter config")
    delta = pd.to_datetime(dataframe[from_date], format=date_format) - pd.to_datetime(dataframe[to_date],
                                                                                      format=date_format)
    dataframe[col_name] = delta.dt.days
    return dataframe


def bucket_formatter(dataframe, col_name, config, runtime_params):
    """
    Convert integers into a user-defined labelled ranges. This formatter modifies the existing column.
    :param dataframe: original dataframe
    :param col_name: column name to be modifies
    :param config: a dictionary containing list of range edges and labels of buckets
    :param runtime_params: command line arguments, not used in this formatter
    :return: dataframe with 'col_name' column modified as per the ranges
    """
    buckets = config.get('buckets')
    bins = list(map(lambda x: float(x), buckets))
    labels = config.get('labels', False)
    include_right = True if str.lower(config.get('include_right', 'true')) == 'true' else False

    categories = pd.cut(dataframe[col_name], bins=bins, labels=labels, right=include_right)
    dataframe[col_name] = categories.values.astype(str)
    return dataframe


def arithmetic_calculation_formatter(dataframe, col_name, format_options, runtime_params):
    """
      Modifies the value of column or generates a new column with mathematically calculated value
      :param dataframe: original dataframe
      :param col_name: name of the new column
      :param format_options : contains columns and operation
      :param runtime_params: command line arguments
      :return: updated dataframe with the modified column
    """

    columns = format_options.get('cols')
    operation = format_options.get('operation')
    value = format_options.get('value')

    valid_operations = ['div', 'mul', 'sub', 'add', 'abs']

    if operation not in valid_operations:
        log.error(f'Unknown arithmetic operation. Valid operations are {valid_operations}')
        raise ValueError

    if operation == 'div':
        dataframe = divide(dataframe, col_name, columns)
        if value is not None:
            dataframe[col_name] = dataframe[col_name].div(value)
    elif operation == 'mul':
        dataframe = multiply(dataframe, col_name, columns)
        if value is not None:
            dataframe[col_name] = dataframe[col_name].mul(value)
    elif operation == 'add':
        dataframe = addition(dataframe, col_name, columns)
        if value is not None:
            dataframe[col_name] = dataframe[col_name].add(value)
    elif operation == 'sub':
        dataframe = subtract(dataframe, col_name, columns)
        if value is not None:
            dataframe[col_name] = dataframe[col_name].sub(value)
    elif operation == 'abs':
        dataframe[col_name] = pd.to_numeric(dataframe[col_name]).abs()
    return dataframe


def fill_empty_values(dataframe, col_name, format_options, runtime_params):
    """
    Fill NA values in column 'col_name' with values taken from another column
    :param dataframe: original dataframe
    :param col_name: column name on which the formatter is applied
    :param format_options: dictionary with a single key called 'column' representing
    the column name which will be used to fill NA values
    :param runtime_params: command line arguments
    :return: new dataframe with NA values replaced in column 'col_name'
    """
    from_column = format_options.get('column')
    if from_column not in dataframe.columns:
        raise KeyError(f"Column '{from_column}' not found.")

    dataframe[col_name] = dataframe[col_name].fillna(dataframe[from_column])
    return dataframe


def fill_empty_values_with_custom_value(dataframe, col_name, format_options, runtime_params):
    """
    NaN rows are filled with constant values
    :param dataframe: original dataframe
    :param col_name: column name on which the formatter is applied
    :param format_options: dictionary key called value (representing
    the values to fill)
    :param runtime_params: command line arguments
    :return: new dataframe with NA values replaced in column 'col_name' with the 'value'
    """
    custom_value = format_options.get('value')
    condition = format_options.get('condition')
    if not pd.Series(col_name).isin(dataframe.columns).all():
        raise KeyError(f"Column '{col_name}' not found.")

    if condition is not None and len(condition) == 2:
        dataframe[col_name] = np.where(np.logical_and(dataframe[col_name].isna(), (
            dataframe[condition.get('match_col')].str.match(pat=condition.get('pattern')))),
                                       custom_value, dataframe[col_name])
    else:
        dataframe[col_name] = dataframe[col_name].fillna(value=custom_value)

    return dataframe


def business_day_formatter(dataframe, new_col_name, format_options, runtime_params):
    """
    returns billing date, i.e., previous business day for a every given date
    :param dataframe: original dataframe
    :param new_col_name: column created after applying formatter
    :param runtime_params: command line arguments
    :return: dataframe with a new column called billing_date for every entry of date column.
    """
    date_col = format_options.get('col')
    date_format = format_options.get('format')
    calendar_country = format_options.get('cal')

    if date_col not in dataframe.columns:
        raise KeyError(f"Column '{date_col}' not found.")

    dataframe[date_col] = pd.to_datetime(dataframe[date_col], format=date_format)
    dataframe[new_col_name] = dataframe[date_col].apply(
        lambda x: get_business_day(x.to_pydatetime(), 'prev', country=calendar_country))
    return dataframe


def split_column_formatter(dataframe, col_name, format_options, runtime_params):
    """
    Adds new columns with values from the given column
    :param dataframe: original dataframe
    :param col_name: name of the column to be splitted
    :param format_options: new column names
    :param runtime_params: Not required for this formatter
    :return: dataframe with new columns having values obtained by splitting original column
    """
    if col_name not in dataframe.columns:
        raise KeyError(f"Column '{col_name}' not found.")
    if dataframe.empty:
        raise ValueError(f"Given Dataframe is Empty.")
    if (dataframe[col_name] == 'na').all():
        return dataframe

    if dataframe[col_name].dtype == object and isinstance(dataframe.iloc[0][col_name], str):
        dataframe[format_options.get('new_col_names')] = dataframe[col_name].str.split(
            format_options.get('delimiter', ','), expand=True)
    else:
        split_df = pd.DataFrame(dataframe[col_name].tolist(), columns=format_options.get('new_col_names'))
        dataframe = pd.concat([dataframe, split_df], axis=1)

    return dataframe


def spacing_formatter(dataframe, col_name, format_options, runtime_params):
    num_of_spaces = format_options.get('spacing')
    if num_of_spaces < 0:
        raise ValueError(f"Spaces cannot be negative")
    if col_name not in dataframe.columns:
        raise KeyError(f"Column '{col_name}' not found.")
    if dataframe.empty:
        raise ValueError(f"Given Dataframe is Empty.")
    else:
        dataframe[col_name] = dataframe[col_name].astype("string")
        dataframe[col_name] = dataframe[col_name].str.ljust(num_of_spaces, " ")
        return dataframe


def add_trailing_zeros_formatter(dataframe, col_name, format_options, runtime_params):
    max_chars = format_options.get('num_of_chars')
    if max_chars < 0:
        raise ValueError(f"Number of characters in a string cannot be negative")
    if col_name not in dataframe.columns:
        raise KeyError(f"Column '{col_name}' not found.")
    if dataframe.empty:
        raise ValueError(f"Given Dataframe is Empty.")
    else:
        dataframe[col_name] = dataframe[col_name].apply(lambda x: str(x).zfill(max_chars))
        return dataframe


def last_date_of_prev_month(dataframe, col_name, format_options, runtime_params):
    """
    This formatter adds a new column which contains last date of last month based on the rumtime date provided by the user.
    the format options contain format of runtime date and output date, which is an input from the user
    col_name is the name of the newly added column
    """

    outdate_format = format_options.get('outdate_format', '%Y%m%d')
    run_date = runtime_params.get('run_date')
    dt_final = run_date.replace(day=1) - timedelta(days=1)
    dataframe[col_name] = str(dt_final.strftime(outdate_format))
    return dataframe


def conditional_replace_formatter(dataframe, col_name, format_options, runtime_params):
    """
        selected rows are filled with column value mentioned
        :param dataframe: original dataframe
        :param col_name: column name on which the formatter is applied
        :param format_options: dictionary key called value (representing
        the values to fill)
        :param runtime_params: command line arguments
        :return: new dataframe with values replaced in column 'col_name' with the 'from_column'
        """
    from_column = format_options.get('from_column')
    condition = format_options.get('condition')

    if from_column not in dataframe.columns:
        raise KeyError(f"Column '{from_column}' not found.")
    match_col = dataframe[condition.get('match_col')].astype(str)
    pattern = str(condition.get('pattern'))
    dataframe[col_name] = np.where(
        match_col.str.match(pat=pattern),
        dataframe[from_column], dataframe[col_name])
    return dataframe


def replace_value(dataframe, col_name, format_options, runtime_params):
    """
    values are replaced with the value specified
    :param dataframe: original dataframe
    :param col_name: column name on which the formatter is applied
    :param format_options: dictionary key called value (representing the from and to value)
        :param runtime_params: command line arguments
    :return: new dataframe with 'from_value' replaced in column 'col_name' with the 'to_value'
    """
    if col_name not in dataframe.columns:
        raise KeyError(f"Column '{col_name}' not found.")
    for from_value, to_value in zip(format_options.get('from_value'), format_options.get('to_value')):
        dataframe[col_name] = dataframe[col_name].replace(
            {from_value: to_value})
    return dataframe


def extract_from_pattern(dataframe, col_name, format_options, runtime_params):
    """
    extract first value from matched pattern
    :param dataframe: original dataframe
    :param col_name: column name on which the formatter is applied
    :param format_options: dictionary key called value
        :param runtime_params: command line arguments
    :return: new dataframe with containing only the email data(if present)
    """
    if col_name not in dataframe.columns:
        raise KeyError(f"Column '{col_name}' not found.")
    pattern = format_options.get('pattern')
    dataframe[col_name] = dataframe[col_name].map(
        lambda x: None if len(re.findall(pattern, str(x))) == 0 else
        (re.findall(pattern, str(x)))[0])
    return dataframe


def index_counter(dataframe, col_name, format_options, runtime_params):
    """
    extract row index from the dataframe
    :param dataframe: original dataframe
    :param col_name: column name on which the formatter is applied
    :param format_options: dictionary key called value
        :param runtime_params: command line arguments
    :return: new dataframe with containing the index of each row in dataframe
    """

    dataframe[col_name] = [i for i in range(len(dataframe))]
    return dataframe


def current_timestamp(dataframe, col_name, format_options, runtime_params):
    """
    add current timestamp value to a column
    :param dataframe: original dataframe
    :param col_name: column name on which the formatter is applied
    :param format_options: dictionary key called value
        :param runtime_params: command line arguments
    :return: new dataframe with containing current timestamp on the specified colmumn
    """
    ts = calendar.timegm(time.gmtime())

    dataframe[col_name] = ts
    return dataframe


def get_running_environment(dataframe, col_name, format_options, runtime_params):
    """
    get current environment value to a column
    :param dataframe: original dataframe
    :param col_name: column name on which the formatter is applied
    :param format_options: dictionary key called value
        :param runtime_params: command line arguments
    :return: new dataframe with containing constant set for the running environment on the specified column
    """

    env = Properties.get_property('ENV')

    constant = format_options.get(env)
    dataframe[col_name] = constant
    return dataframe


def runtime_date(dataframe, col_name, format_options, runtime_params):
    """
        create a new row with runtime date value
        :param dataframe: original dataframe
        :param col_name: column name on which the formatter is applied
        :param format_options: dictionary key called value (representing
        the values to fill)
        :param runtime_params: command line arguments
        :return: new dataframe with NA values replaced in column 'col_name' with the 'value'
        """
    dataframe[col_name] = runtime_params['run_date']
    return date_formatter(dataframe, col_name, {'src': '%m%d%Y', 'des': format_options.get('des')}, {})


def add_uuid_col(dataframe, col_name, format_options, runtime_params):
    """
    Adds a new column with UUIDs
    :param dataframe: original dataframe
    :param col_name: name of the new column to be added
    :param format_options: None
    :param runtime_params: Not required for this formatter
    :return: dataframe with a new UUID column
    """
    dataframe[col_name] = [uuid.uuid4() for _ in range(len(dataframe.index))]
    return dataframe


def sub_string(dataframe, col_name, format_options, runtime_params):
    """
        get a substring from the column value
        :param dataframe: original dataframe
        :param col_name: name of the new column to be added
        :param format_options: represent start and end index to get the substring from the string
        :param runtime_params: Not required for this formatter
        :return: dataframe with a new substring value of that column
        """
    start = format_options.get('start', None)
    end = format_options.get('end', None)
    dataframe[col_name] = dataframe[col_name].astype(str).str[start:end]
    return dataframe


def float_precision(dataframe, col_name, format_options, runtime_params):
    """
    get floating column precision by certain decimal after point
    :param dataframe: original dataframe
    :param col_name: the column to be updated
    :param format_options: dictionary of key value pair representing the precision to be used
    :param runtime_params: Not required for this formatter
    :return: dataframe with a float point values formatted
    """
    precision = format_options.get('precision')
    dataframe[col_name] = dataframe[col_name].map(lambda x: float(f"%.{precision}f" % x))
    return dataframe


def drop_duplicates(dataframe, col_name, format_options, runtime_params):
    """
    drop duplicate rows
    :param dataframe: original dataframe
    :param col_name: the column to be compared for duplicate values
    :param format_options: dictionary of key value pair representing which duplicates to drop
    :param runtime_params: Not required for this formatter
    :return: dataframe with a float point values formatted
    """
    valid_vals = ['first', 'last', False]
    keep_opt = format_options.get('keep')
    if keep_opt not in valid_vals:
        keep_opt = 'first'
    return dataframe.drop_duplicates(subset=[col_name], keep=keep_opt)


def prefix_string_formatter(dataframe, col_name, config, runtime_params):
    """
    Concatenates the provided columns, appends the string and adds as a new column to the dataframe
    :param dataframe: original data frame
    :param col_name: name of the new column
    :param columns: list of names of columns to be concatenated
    :param runtime_params: command line arguments
    :return: dataframe with a new concatenated column
    """
    default_separator = ''
    separator = config.get('separator', default_separator)
    columns = config.get('columns')
    start = config.get('prefix', None)

    if any([column not in dataframe for column in columns]):
        log.error('Unknown column passed to concat formatter')
        raise ValueError

    dataframe[col_name] = dataframe[columns].astype(str).agg(separator.join, axis=1)
    dataframe[col_name] = start + dataframe[col_name].astype(str)

    return dataframe


formatter_map = {
    'date': date_formatter,
    'float': float_formatter,
    'concat': concat_formatter,
    'constant': constant_formatter,
    'constant-date': constant_date_formatter,
    'duplicate': duplicate_column_formatter,
    'decryption': decryption_formatter,
    'encryption': encryption_formatter,
    'group-percentage': group_percentage_formatter,
    'sum': sum_value_formatter,
    'date-diff': date_diff_formatter,
    'bucket': bucket_formatter,
    'arithmetic_calc': arithmetic_calculation_formatter,
    'fill_empty_values': fill_empty_values,
    'fill_empty_values_with_custom_value': fill_empty_values_with_custom_value,
    'replace_value': replace_value,
    'runtime_date': runtime_date,
    'uuid': add_uuid_col,
    'sub_string': sub_string,
    'conditional_replace_formatter': conditional_replace_formatter,
    'bus_day': business_day_formatter,
    'split_col': split_column_formatter,
    'float_precision': float_precision,
    'extract_from_pattern': extract_from_pattern,
    'index_counter': index_counter,
    'add_space': spacing_formatter,
    'add_trailing_zeros': add_trailing_zeros_formatter,
    'last_date_of_prev_month': last_date_of_prev_month,
    'current_timestamp': current_timestamp,
    'get_running_environment': get_running_environment,
    'drop_duplicates': drop_duplicates,
    'prefix_string': prefix_string_formatter,

}


def get_formatter_from_type(formatter_type):
    """
     gets an formatter, returns formatter function

     :param formatter_type : name/type of the formatter
    """
    return formatter_map.get(formatter_type)

def add_formatter(formatter_type, formatter):
    """
     adds a new formatter, adding for flexibility for users of ingen

     :param formatter_type : name/type of the formatter
     :param formatter : formatter function
    """
    return formatter_map.update( {formatter_type: formatter} )
