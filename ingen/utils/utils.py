#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import argparse
import datetime
import operator
from datetime import date

import numpy as np
import pandas as pd

import holidays

from ingen.utils.properties import properties


def holiday_calendar(country=None, year=None):
    """
        A utility method to get holiday calendar for country configured in property_instance file for given calendar year.

        Returns HolidayBase object which is a dict like object

        The key of the object is the date of the holiday and the value is the name
        of the holiday itself. When passing the date as a key, the date can be
        expressed as one of the following formats:
        * :class:`datetime.date`,
        * :class:`datetime.datetime`,
        * a :class:`str` of any format recognized by :func:`dateutil.parser.parse`,
        * or a :class:`float` or :class:`int` representing a POSIX timestamp.
        """

    if year is None:
        today = date.today()
        year = today.year
    country = properties.get_property('holiday_country', country)
    if country is None:
        raise ValueError(f'a valid country code is required to get holiday_calendar. {country} is not valid.')
    holiday_country = holidays.country_holidays(country, years=year)
    return holiday_country


def get_business_day(input_date, offset='next', country=None):
    """
            A utility method to get business date for passed date.
            If passed date is a public holiday, get previous or next business day
            depending upon if next or prev is passed

            """
    holiday_dict = holiday_calendar(country=country, year=input_date.year)
    if input_date in holiday_dict or input_date.weekday() > 4:
        if offset == 'prev':
            return get_business_day(input_date - datetime.timedelta(1), offset, country)
        else:
            return get_business_day(input_date + datetime.timedelta(1), offset, country)
    else:
        return input_date


ops = {
    '==': operator.eq,
    '!=': operator.ne,
    '<': operator.lt,
    '<=': operator.le,
    '>': operator.gt,
    '>=': operator.ge,
    'in': operator.contains
}


def compare(dataframe, match_col, compare_lst):
    if match_col not in dataframe:
        raise ValueError(f'Column {match_col} not found in dataframe')
    elif not compare_lst or len(compare_lst) != 2:
        raise ValueError("Comparison input does not exist or is incomplete")

    try:
        compare_oper = ops[compare_lst[0]]
    except KeyError:
        raise ValueError(f"Operator {compare_lst[0]} is not valid")

    compare_val = compare_lst[1]
    cond_results = pd.Series(False, index=np.arange(dataframe[match_col].size), name=None)  
    if compare_val is None:
        if compare_oper == operator.eq:
            cond_results = dataframe[match_col].isna()
        elif compare_oper == operator.ne:
            cond_results = dataframe[match_col].notna()
    elif compare_oper is operator.contains:
        if not isinstance(compare_val, list):
            raise ValueError("The second value under compare isn't in list format")
        cond_results = dataframe[match_col].isin(compare_val)
    else:
        cond_results = compare_oper(dataframe[match_col], compare_val)
    
    cond_results.name = None
    return cond_results


class KeyValue(argparse.Action):
    """
    A utility class to create dict-like key value pairs from command lines arguments

    e.g, Following command lines argument
    --query_params date=12/09/1995 name=merry table=position

    will be converted into a dictionary
    query_params = { 'date': '12/09/1995', 'name': 'merry', 'table': 'position }
    """

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, dict())

        for value in values:
            key, value = value.split('=')
            getattr(namespace, self.dest)[key] = value


class KeyValueOrString(argparse.Action):
    """
    A utility class to handle cases where a command line argument is either a single value, a list of key value pairs
    separated by = or None.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            setattr(namespace, self.dest, None)
        elif len(values) == 1 and '=' not in values[0]:
            setattr(namespace, self.dest, values[0])
        else:
            setattr(namespace, self.dest, dict())

            for value in values:
                key, value = value.split('=', 1)
                getattr(namespace, self.dest)[key] = value
