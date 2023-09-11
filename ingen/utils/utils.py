#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import argparse
import datetime
from datetime import date

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
