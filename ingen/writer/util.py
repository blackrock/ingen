""""
Utility class to add on custom functions for adding user defined header and footer as required
"""
#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import datetime
from datetime import date
from datetime import timedelta


def get_custom_value(props, df, run_date):
    """
    Evaluates the values corresponding to the functions defined in yml and return the custom footer/header as a string.
    :param props                     SQL query
    :param df                        dataframe object of records stored in output file.
    :param run_date                  date used via command line while invoking
    :return: custom header/footer as a string in the order defined in yml file.
    """
    custom_string = ""
    for prop in props:
        for key, value in prop.items():
            custom_function = get_type(key)
            custom_string = custom_string + custom_function(value, df=df, run_date=run_date)
    return custom_string


def get_constant(value, **kwargs):
    """
    Evaluates the values corresponding to the functions defined in yml and return the custom footer/header as a string.
    :param value :                    constant string
    :return: return the constant value as a string
    """
    return str(value)


def get_filler(white_spaces, **kwargs):
    """
    Evaluates the values corresponding to the functions defined in yml and return the custom footer/header as a string.
    :param white_spaces:                     number of white spaces intended in header/footer
    :return: a string with white spaces equivalent to white_spaces
    """
    filler_string = ""
    return filler_string.ljust(white_spaces)


def get_date(date_format, **kwargs):
    """
    Evaluates the values corresponding to the functions defined in yml and return the custom footer/header as a string.
    :param date_format :                    format of date required
    :return: date as a string in format as date_format
    """
    return date.today().strftime(date_format)


def get_row_count(row_count_prop, **kwargs):
    """
    Evaluates the values corresponding to the functions defined in yml and return the custom footer/header as a string.
    :param row_count_prop: dictionary containing values to calculate row count of the output file.
    :return: count of records in output file with left_padding which will right allign the result and fills
    remaining space on left side with 0.
    header: represents the number of lines the user wants to add from the header to the total row count.
            if header = bool & True:
                row count= row_count +1
            else:
                row count= row_count+ header(int value)
    footer: represents the number of lines the user wants to add from the footer to the total row count.
            if footer = bool & True:
                row count= row_count +1
            else:
                row count= row_count+ footer(int value)
    """
    df = kwargs.get('df')
    include_header = 0
    include_footer = 0

    left_padding = row_count_prop['left_padding']
    if 'header' in row_count_prop and row_count_prop['header'] is True:
        include_header = 1
    elif 'header' in row_count_prop:
        include_header = row_count_prop.get('header')
    if 'footer' in row_count_prop and row_count_prop['footer'] is True:
        include_footer = 1
    elif 'footer' in row_count_prop:
        include_footer = row_count_prop.get('footer')
    columns = str(df.shape[0] + include_footer + include_header)
    return str(columns.rjust(left_padding, '0'))


def get_run_date(run_date_format, **kwargs):
    """
    Evaluates the values corresponding to the functions defined in yml and return the custom footer/header as a string.
    :param run_date_format:           format of date required
    :return: run_date of the file in the format specified.
    """

    run_date = kwargs.get('run_date')
    return run_date.strftime(run_date_format)


def get_new_line(line, **kwargs):
    """
    Takes a boolean input and adds a new line if bool value is true
    """
    if line:
        newline = '\n'
        return newline


def sum_of_substr(props, **kwargs):
    """
    takes column name, starting and ending index for substring as input and returns sum of all substring values of that column
    """
    df = kwargs.get('df')
    start = props['start']
    end = props['end']
    char_count = props['char_count']
    col = props['col_name']
    sum_str = df[col].str[start:end].astype(int).sum()
    return str(sum_str).rjust(char_count, '0')


def col_sum(col_name, **kwargs):
    """
    returns the sum of all values of a dataframe column 
    """
    df = kwargs.get('df')
    total = df[col_name].astype(int).sum()
    return str(total)


def last_date_of_prev_month(props, **kwargs):
    """
    Returns last date of the last month in the user-desired format based on the given run date
    """
    dt_format = props['dt_format']
    run_date = kwargs.get('run_date')
    final_date = run_date.replace(day=1) - timedelta(days=1)
    return str(final_date.strftime(dt_format))


def first_date_of_current_month(props, **kwargs):
    """
    Returns first date of the current month in the user-desired format based on the given run date
    """
    run_date = kwargs.get('run_date')
    dt_format = props['dt_format']
    final_date = run_date.replace(day=1)
    return str(final_date.strftime(dt_format))


def last_date_of_current_month(props, **kwargs):
    """
    Returns last date of the current month in the user-desired format based on the given run date
    """
    dt_format = props['dt_format']
    run_date = kwargs.get('run_date')
    next_month_jump = run_date.replace(day=28) + datetime.timedelta(days=4)
    final_date = next_month_jump - datetime.timedelta(days=next_month_jump.day)
    return str(final_date.strftime(dt_format))


def first_date_of_next_month(props, **kwargs):
    """
    Returns first date of the next month in the user-desired format based on the given run date
    """
    run_date = kwargs.get('run_date')
    dt_format = props['dt_format']
    final_date = (run_date.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
    return str(final_date.strftime(dt_format))


value_map = {
    'date': get_date,
    'run_date': get_run_date,
    'constant': get_constant,
    'filler': get_filler,
    'row_count': get_row_count,
    'add_new_line': get_new_line,
    'sum': col_sum,
    'sum_of_substr': sum_of_substr,
    'first_date_of_current_month': first_date_of_current_month,
    'last_date_of_prev_month': last_date_of_prev_month,
    'last_date_of_current_month': last_date_of_current_month,
    'first_date_of_next_month': first_date_of_next_month
}


def get_type(custom_type):
    return value_map.get(custom_type)
