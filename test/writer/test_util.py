#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pandas as pd
from datetime import datetime, date

from ingen.writer.writer import (get_filler, get_constant, get_date, get_row_count, 
                                get_run_date, get_type, get_new_line, col_sum, 
                                sum_of_substr, last_date_of_prev_month, 
                                first_date_of_current_month, last_date_of_current_month, 
                                first_date_of_next_month)


class TestUtil:

    def test_filler(self):
        filler_space = 5
        filler_value = get_filler(filler_space)
        assert filler_value == "     "

    def test_constant(self):
        value = "MOCK VALUE"
        constant_value = get_constant(value)
        assert constant_value == "MOCK VALUE"

    def test_date(self):
        date_format = "%Y%m%d"
        date_value = get_date(date_format)
        assert date_value == date.today().strftime(date_format)

    def test_row_count_with_both_header_and_footer(self):
        row_count_props = {'left_padding': 4, 'header': 2, 'footer': True}
        data = [1, 2, 3, 4, 5, 6]
        mock_df = pd.DataFrame(data)
        row_count_value = get_row_count(row_count_props, df=mock_df)
        assert row_count_value == "0009"

    def test_row_count_with_either_header_or_footer(self):
        row_count_props = {'left_padding': 4, 'footer': True}
        data = [1, 2, 3, 4, 5, 6]
        mock_df = pd.DataFrame(data)
        row_count_value = get_row_count(row_count_props, df=mock_df)
        assert row_count_value == "0007"

    def test_row_count_with_integer_header_footer_values(self):
        row_count_props = {'left_padding': 4, 'header': 2, 'footer': 3}
        data = [1, 2, 3, 4, 5, 6]
        mock_df = pd.DataFrame(data)
        row_count_value = get_row_count(row_count_props, df=mock_df)
        assert row_count_value == "0011"

    def test_row_count_without_header_and_footer(self):
        row_count_props = {'left_padding': 4}
        data = [1, 2, 3, 4, 5, 6]
        mock_df = pd.DataFrame(data)
        row_count_value = get_row_count(row_count_props, df=mock_df)
        assert row_count_value == "0006"

    def test_run_date(self):
        mock_run_date = datetime.strptime("20211202", "%Y%m%d")
        mock_run_date_format = "%Y%m%d"
        run_date_value = get_run_date(mock_run_date_format, run_date=mock_run_date)
        assert run_date_value == "20211202"

    def test_get_type(self):
        custom_value = 'date'
        assert get_type(custom_value) == get_date
        custom_value = 'filler'
        assert get_type(custom_value) == get_filler

    def test_get_newline(self):
        line = True
        new_line = '\n'
        assert get_new_line(line) == new_line

    def test_col_sum(self):
        mock_df = pd.DataFrame({'row': ['1', '2', '3', '4', '5', '6', '7']})
        sum_result = col_sum('row', df=mock_df)
        assert sum_result == "28"

    def test_sum_of_substr(self):
        mock_df = pd.DataFrame({'State': ['Arizona AZ', 'Georgia GG', 'Newyork NY', 'Indiana IN', 'Florida FL'],
                                'Score': ['00000000000062', '000000000047', '0000000000055', '000000000000074',
                                          '00000000000031']})
        props = {
            'col_name': 'Score',
            'start': 6,
            'end': 15,
            'char_count': 10
        }
        sum_str = sum_of_substr(props, df=mock_df)
        assert sum_str == '0000000269'

    def test_last_date_of_prev_month(self):
        mock_run_date = datetime.strptime("20211202", "%Y%m%d")
        props = {
            'dt_format': '%m/%d/%Y'
        }
        result = last_date_of_prev_month(props, run_date=mock_run_date)
        print(result)
        assert result == '11/30/2021'

    def test_last_date_of_prev_month_julian(self):
        mock_run_date = datetime.strptime("20211202", "%Y%m%d")
        props = {
            'dt_format': '%Y%j'
        }
        result = last_date_of_prev_month(props, run_date=mock_run_date)
        print(result)
        assert result == '2021334'

    def test_last_date_of_prev_month_julian_for_January_month(self):
        mock_run_date = datetime.strptime("20210120", "%Y%m%d")
        props = {
            'dt_format': '%Y%j'
        }
        result = last_date_of_prev_month(props, run_date=mock_run_date)
        assert result == '2020366'

    def test_last_date_of_prev_month_for_January_month(self):
        mock_run_date = datetime.strptime("20210101", "%Y%m%d")
        props = {
            'dt_format': '%m/%d/%Y'
        }
        result = last_date_of_prev_month(props, run_date=mock_run_date)
        assert result == '12/31/2020'

    def test_first_date_of_current_month(self):
        mock_run_date = datetime.strptime("20211202", "%Y%m%d")
        props = {
            'dt_format': '%m/%d/%Y'
        }
        result = first_date_of_current_month(props, run_date=mock_run_date)
        assert result == '12/01/2021'

    def test_last_date_of_current_month(self):
        mock_run_date = datetime.strptime("20211022", "%Y%m%d")
        props = {
            'dt_format': '%m/%d/%Y'
        }
        result = last_date_of_current_month(props, run_date=mock_run_date)
        assert result == '10/31/2021'
        print(result)

    def test_last_date_of_current_month_julian_date(self):
        mock_run_date = datetime.strptime("20211022", "%Y%m%d")
        props = {
            'dt_format': '%Y%j'
        }
        result = last_date_of_current_month(props, run_date=mock_run_date)
        assert result == '2021304'

    def test_first_date_of_next_month(self):
        mock_run_date = datetime.strptime("20211202", "%Y%m%d")
        props = {
            'dt_format': '%m/%d/%Y'
        }
        result = first_date_of_next_month(props, run_date=mock_run_date)
        assert result == '01/01/2022'