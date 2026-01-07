#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from datetime import date
from unittest.mock import patch

from ingen.formatters.common_formatters import *
from ingen.utils.utils import holiday_calendar


class TestCommonFormatters(unittest.TestCase):

    def test_column_filter(self):
        dataframe = pd.DataFrame({
            'name': ['Jon', 'Arya', 'Cersie'],
            'family': ['Stark', 'Stark', 'Lannister']
        })
        required_column_names = ['name', 'family']
        filtered_dataframe = column_filter(dataframe, required_column_names)
        self.assertListEqual(required_column_names, list(filtered_dataframe.columns))

    def test_column_filter_with_required_column_order(self):
        dataframe = pd.DataFrame({
            'name': ['Jon', 'Arya', 'Cersie'],
            'family': ['Stark', 'Stark', 'Lannister'],
            'kingdom': ['Westeros', 'Vale', 'Volantis'],
            'season': ['season1', 'season2', 'season3']
        })
        required_column_names = ['kingdom', 'family', 'name']
        filtered_dataframe = column_filter(dataframe, required_column_names)
        self.assertListEqual(required_column_names, list(filtered_dataframe.columns))

    def test_column_filter_with_extra_columns(self):
        dataframe = pd.DataFrame({
            'name': ['Jon', 'Arya', 'Cersie'],
            'family': ['Targaryen', 'Stark', 'Lannister'],
            'father': ['Eddard Stark', 'Rhaegar Targaryen', 'Tywin Lannister']
        })
        required_column_names = ['name', 'family']
        filtered_dataframe = column_filter(dataframe, required_column_names)
        self.assertListEqual(required_column_names, list(filtered_dataframe.columns))

    def test_name_formatter_changes_column_label(self):
        df = pd.DataFrame({
            "date": ["12/09/1995", "13/09/1995", "14/09/1995"],
            "price": [113.452, 112.243, 45.908],
            "ticker": ["APL", "TCS", "TATA"]
        })
        id_name_map = {
            "date": "DATE",
            "price": "CURR PRICE",
            "ticker": "SYMBOL"
        }
        name_formatter(df, id_name_map)
        expected_column_labels = list(id_name_map.values())
        self.assertListEqual(expected_column_labels, list(df.columns))

    def test_date_formatter_formats_date(self):
        df = pd.DataFrame({
            "date": ["09091995", "09101995", "09111995", None]
        })
        date_format_dict = {"src": "%d%m%Y", "des": "%Y-%m-%d"}
        expected_date_column = pd.Series(["1995-09-09", "1995-10-09", "1995-11-09", ""])
        date_formatter(df, 'date', date_format_dict, {})
        self.assertTrue(pd.Series.equals(expected_date_column, df['date']))

    def test_date_formatter_with_none(self):
        df = pd.DataFrame({
            "date": ["09091995", None]
        })
        date_format_dict = {"src": "%d%m%Y", "des": "%Y-%m-%d"}
        expected_date_column = pd.Series(["1995-09-09", ""])
        date_formatter(df, 'date', date_format_dict, {})
        self.assertTrue(pd.Series.equals(expected_date_column, df['date']))

    @patch.object(Cryptor, "_Cryptor__get_key", return_value=(bytes('34DDA783B8C979C881E0EB3C8185825B', 'utf-8'), 3))
    @patch.object(Cryptor, "_Cryptor__get_hmac_key",
                  return_value=(bytes('e4ee804adfbc82376daba92960449d', 'utf-8'), 3))
    def test_encryption_formatter(self, mock_get_key, mock_get_hmac_key):
        """
        Unit test the encryption formatter.
        :return: None
        """
        df = pd.DataFrame({"account_number": ["1232323", "23332211"]})
        en_df = encryption_formatter(df, "account_number", "test", None)
        self.assertEqual(list(en_df.columns), ["account_number"])

    @patch.object(Cryptor, "_Cryptor__get_key", return_value=(bytes('34DDA783B8C979C881E0EB3C8185825B', 'utf-8'), 3))
    @patch.object(Cryptor, "_Cryptor__get_hmac_key",
                  return_value=(bytes('e4ee804adfbc82376daba92960449d', 'utf-8'), 3))
    def test_decryption_formatter(self, mock_get_key, mock_hmac_key):
        """
        Unit test the decryption formatter.
        :return: None
        """
        df = pd.DataFrame({"account_number": ['eyJjaXBoZXIiOiAiamtNang4Zz0iLCAibm9uY2UiOiAiWHNaMUwxcTZGeGs9IiwgIm1hYyI'
                                              '6ICJkZGFkYmU1NzdkMGRhZDZhMGEwNWM4OTIzYzcyMTdmYjA1YWYxZGM0NzhmOGJmYzg4N2'
                                              'Y2OGIxMmMxNmY3ZDRhIiwgImtleV92ZXJzaW9uIjogMywgImhtYWNfdmVyc2lvbiI6IDN9',
                                              'eyJjaXBoZXIiOiAieXlMWWg1RT0iLCAibm9uY2UiOiAiUkdDdDhKZzg4NTQ9IiwgIm1hYyI'
                                              '6ICJjNjcxZjBkNTEyZjljOWFiNGIzNTE5MTFjYWYwNmNjNjdlZWZiZGJlZDRiMzEyOWNlNz'
                                              'c3YjM0ZjkxNTA3OTlkIiwgImtleV92ZXJzaW9uIjogMywgImhtYWNfdmVyc2lvbiI6IDN9']})
        decrypt_df = decryption_formatter(df, "account_number", "test", None)
        data = decrypt_df['account_number'].to_numpy()
        self.assertEqual(list(data), ["Hello", "World"])
        self.assertEqual(list(decrypt_df.columns), ["account_number"])

    def test_date_with_char_string(self):
        df = pd.DataFrame({
            "date": ["09091995", "abc"]
        })
        date_format_dict = {"src": "%d%m%Y", "des": "%Y-%m-%d"}
        with self.assertRaises(ValueError):
            date_formatter(df, 'date', date_format_dict, {})

    def test_float_formatter_applies_given_format(self):
        df = pd.DataFrame({
            "price": [113.452, 1212.243, 45.908]
        })
        float_format = "${:,.2f}"
        expected_price_column = pd.Series(["$113.45", "$1,212.24", "$45.91"])
        float_formatter(df, 'price', float_format, {})
        self.assertTrue(pd.Series.equals(df['price'], expected_price_column))

    def test_prefix_string_formatter(self):
        df = pd.DataFrame({
            "account_number": ["13419202", "13419201", "13419200"],
            "quantity": ['113', '112', '45'],

        })
        output_column = 'LOT_ID'
        input_columns = ['account_number', 'quantity']
        param = {
            'columns': input_columns,
            'prefix': '161'
        }
        expected_output_column = pd.Series(
            ["16113419202113", "16113419201112", "1611341920045"])
        prefix_string_formatter(df, output_column, param, {})
        self.assertTrue(pd.Series.equals(df['LOT_ID'], expected_output_column))

    def test_concat_formatter(self):
        df = pd.DataFrame({
            "account_number": ["13419202", "13419201", "13419200"],
            "quantity": ['113.452', '112.243', '45.908'],
            "cusip": ["G0250X107", "G0250X105", "G0250X103"]
        })
        output_column = 'LOT_ID'
        input_columns = ['account_number', 'quantity', 'cusip']
        param = {
            'columns': input_columns,
            'separator': '_'
        }
        expected_output_column = pd.Series(
            ["13419202_113.452_G0250X107", "13419201_112.243_G0250X105", "13419200_45.908_G0250X103"])
        concat_formatter(df, output_column, param, {})
        self.assertTrue(pd.Series.equals(df['LOT_ID'], expected_output_column))

    def test_concat_formatter_with_different_data_types(self):
        data = pd.DataFrame({
            'strings': list('abcd'),
            'numbers': [1, 2, 3, 4]
        })
        new_col_name = 'test column'
        concatenating_columns = ['strings', 'numbers']
        param = {
            'columns': concatenating_columns,
            'separator': '_'
        }
        expected_data = data.copy()
        expected_data[new_col_name] = ['a_1', 'b_2', 'c_3', 'd_4']

        formatted_data = concat_formatter(data, new_col_name, param, {})

        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_business_day_formatter(self):
        sample_data = pd.DataFrame({'date': ['01/05/2022', '02/05/2022', '03/05/2022', '04/05/2022']})
        sample_data['date'] = pd.to_datetime(sample_data['date'], format='%d/%m/%Y')

        new_col_name = 'billing_date'
        format_options = {
            'col': 'date',
            'format': '%d/%m/%Y',
            'cal': 'US'
        }
        billing_date_val = ['29/04/2022', '02/05/2022', '03/05/2022', '04/05/2022']

        expected_data = sample_data.copy()
        expected_data[new_col_name] = pd.to_datetime(billing_date_val, format='%d/%m/%Y')

        formatted_data = business_day_formatter(sample_data, new_col_name, format_options, {})
        print('formatted', formatted_data)
        print(expected_data)
        pd.testing.assert_frame_equal(expected_data, formatted_data, check_dtype=False)

    def test_business_day_formatter_incorrect_column(self):
        sample_data = pd.DataFrame({'date': ['01/05/2022', '02/05/2022', '03/05/2022', '04/05/2022']})
        sample_data['date'] = pd.to_datetime(sample_data['date'], format='%d/%m/%Y')

        new_col_name = 'billing_date'
        format_options = {
            'col': 'days',
            'format': '%d/%m/%Y',
            'cal': 'US'
        }
        billing_date_val = ['29/04/2022', '02/05/2022', '03/05/2022', '04/05/2022']

        expected_data = sample_data.copy()
        expected_data[new_col_name] = pd.to_datetime(billing_date_val, format='%d/%m/%Y')
        with self.assertRaisesRegex(KeyError, "Column 'days' not found."):
            business_day_formatter(sample_data, new_col_name, format_options, {})

    def test_last_date_of_prev_month(self):
        data = pd.DataFrame({'name': ['Samridhi', 'Sanwari', 'Megha'],
                             'subject': [['hindi', 'english'],
                                         ['geography', 'sanskrit'],
                                         ['civics', 'history']]
                             })
        format_options = {
            'outdate_format': '%Y%m%d%Y%m%d'
        }
        expected_data = pd.DataFrame({'name': ['Samridhi', 'Sanwari', 'Megha'],
                                      'subject': [['hindi', 'english'],
                                                  ['geography', 'sanskrit'],
                                                  ['civics', 'history']],
                                      'Date': ['2021113020211130', '2021113020211130', '2021113020211130']
                                      })
        formatted_data = last_date_of_prev_month(data, 'Date', format_options,
                                                 {'run_date': date(year=2021, month=12, day=3)})
        pd.testing.assert_frame_equal(expected_data, formatted_data, check_dtype=False)

    def test_split_column_formatter_with_list(self):

        data = pd.DataFrame({'name': ['Samridhi', 'Sanwari', 'Megha'],
                             'subject': [['hindi', 'english'],
                                         ['geography', 'sanskrit'],
                                         ['civics', 'history']]
                             })
        format_options = {
            'new_col_names': ['sub1', 'sub2']
        }
        expected_data = pd.DataFrame({'name': ['Samridhi', 'Sanwari', 'Megha'],
                                      'subject': [['hindi', 'english'],
                                                  ['geography', 'sanskrit'],
                                                  ['civics', 'history']],
                                      'sub1': ['hindi', 'geography', 'civics'],
                                      'sub2': ['english', 'sanskrit', 'history']
                                      })

        formatted_data = split_column_formatter(data, 'subject', format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data, check_dtype=False, check_column_type=False)

    def test_split_column_formatter_with_string(self):
        data = pd.DataFrame({'name': ['Samridhi', 'Sanwari', 'Megha'],
                             'subject': ['hindi,english', 'geography,sanskrit', 'civics,history']})

        format_options = {
            'new_col_names': ['sub1', 'sub2'],
            'delimiter': ','
        }
        expected_data = pd.DataFrame({'name': ['Samridhi', 'Sanwari', 'Megha'],
                                      'subject': ['hindi,english', 'geography,sanskrit', 'civics,history'],
                                      'sub1': ['hindi', 'geography', 'civics'],
                                      'sub2': ['english', 'sanskrit', 'history']
                                      })

        formatted_data = split_column_formatter(data, 'subject', format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data, check_dtype=False, check_column_type=False)

    def test_split_column_formatter_wrong_column(self):
        data = pd.DataFrame({'name': ['Samridhi', 'Sanwari', 'Megha'],
                             'subject': ['hindi,english', 'geography,sanskrit', 'civics,history']})

        format_options = {
            'new_col_names': ['sub1', 'sub2']
        }

        with self.assertRaisesRegex(KeyError, "Column 'Age' not found."):
            split_column_formatter(data, 'Age', format_options, {})

    def test_split_column_formatter_empty_dataframe(self):
        col_names = ['subject', 'name']
        data = pd.DataFrame(columns=col_names)
        format_options = {
            'new_col_names': ['sub1', 'sub2']
        }
        with self.assertRaisesRegex(ValueError, "Given Dataframe is Empty"):
            split_column_formatter(data, 'subject', format_options, {})

    def test_add_trailing_zeros_formatter(self):
        data = pd.DataFrame({'name': [1234, 2345, '86007'],
                             'subject': ['hindi,english', 'geography,sanskrit', 'civics,history']})
        format_options = {
            'num_of_chars': 10
        }
        expected_data = pd.DataFrame({'name': ['0000001234', '0000002345', '0000086007'],
                                      'subject': ['hindi,english', 'geography,sanskrit', 'civics,history']})

        formatted_data = add_trailing_zeros_formatter(data, 'name', format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data, check_dtype=False, check_column_type=False)

    def test_add_trailing_zeros_formatter_empty_dataframe(self):
        col_names = ['name', 'subject']
        data = pd.DataFrame(columns=col_names)
        format_options = {
            'num_of_chars': 10
        }
        with self.assertRaisesRegex(ValueError, "Given Dataframe is Empty"):
            add_trailing_zeros_formatter(data, 'name', format_options, {})

    def test_add_trailing_zeros_formatter_wrong_col(self):
        data = pd.DataFrame({'name': ['1234', '2345', '86007'],
                             'subject': ['hindi,english', 'geography,sanskrit', 'civics,history']})
        format_options = {
            'num_of_chars': 10
        }
        with self.assertRaisesRegex(KeyError, "Column 'Age' not found."):
            add_trailing_zeros_formatter(data, 'Age', format_options, {})

    def test_add_trailing_zeros_formatter_wrong_number_of_chars(self):
        data = pd.DataFrame({'name': ['1234', '2345', '86007'],
                             'subject': ['hindi,english', 'geography,sanskrit', 'civics,history']})
        format_options = {
            'num_of_chars': -10
        }
        with self.assertRaisesRegex(ValueError, "Number of characters in a string cannot be negative"):
            add_trailing_zeros_formatter(data, 'name', format_options, {})

    def test_spacing_formatter(self):
        data = pd.DataFrame({'name': [1234, 2345, '86007'],
                             'subject': ['hindi,english', 'geography,sanskrit', 'civics,history']})
        format_options = {
            'spacing': 20
        }
        expected_data = pd.DataFrame({'name': ['1234                ', '2345                ', '86007               '],
                                      'subject': ['hindi,english', 'geography,sanskrit', 'civics,history']})

        formatted_data = spacing_formatter(data, 'name', format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data, check_dtype=False, check_column_type=False)

    def test_spacing_formatter_empty_dataframe(self):
        col_names = ['name', 'subject']
        data = pd.DataFrame(columns=col_names)
        format_options = {
            'spacing': 20
        }
        with self.assertRaisesRegex(ValueError, "Given Dataframe is Empty"):
            spacing_formatter(data, 'name', format_options, {})

    def test_spacing_formatter_wrong_col(self):
        data = pd.DataFrame({'name': ['1234', '2345', '86007'],
                             'subject': ['hindi,english', 'geography,sanskrit', 'civics,history']})
        format_options = {
            'spacing': 20
        }
        with self.assertRaisesRegex(KeyError, "Column 'Age' not found."):
            spacing_formatter(data, 'Age', format_options, {})

    def test_spacing_formatter_wrong_number_of_chars(self):
        data = pd.DataFrame({'name': ['1234', '2345', '86007'],
                             'subject': ['hindi,english', 'geography,sanskrit', 'civics,history']})
        format_options = {
            'spacing': -10
        }
        with self.assertRaisesRegex(ValueError, "Spaces cannot be negative"):
            spacing_formatter(data, 'name', format_options, {})

    def test_concat_formatter_with_only_one_column(self):
        data = pd.DataFrame({
            'name': ['Arya', 'Jon', 'Khalisi'],
            'gender': ['F', 'M', 'F']
        })
        new_col_name = 'concatenated column'
        concatenating_columns = ['gender']
        param = {
            'columns': concatenating_columns,
            'separator': '_'
        }

        expected_data = data.copy()
        expected_data[new_col_name] = data.gender

        formatted_data = concat_formatter(data, new_col_name, param, {})

        pd.testing.assert_frame_equal(expected_data, formatted_data)

    @patch('ingen.formatters.common_formatters.log')
    def test_concat_formatter_with_unknown_column(self, mock_logging):
        data = pd.DataFrame({
            'name': ['Arya', 'Jon', 'Khalisi'],
            'gender': ['F', 'M', 'F']
        })
        new_col_name = 'concatenated column'
        concatenating_columns = ['age']
        param = {
            'columns': concatenating_columns,
            'separator': '_'
        }

        with self.assertRaises(ValueError):
            concat_formatter(data, new_col_name, param, {})

        mock_logging.error.assert_called_with('Unknown column passed to concat formatter')

    def test_concat_formatter_without_seperator(self):
        data = pd.DataFrame({
            'name': ['Arya', 'Jon', 'Khalisi'],
            'gender': ['F', 'M', 'F']
        })
        new_col_name = 'concatenated column'
        concatenating_columns = ['gender']
        param = {
            'columns': concatenating_columns
        }

        expected_data = data.copy()
        expected_data[new_col_name] = data.gender

        formatted_data = concat_formatter(data, new_col_name, param, {})

        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_get_formatter_name_returns_date_formatter(self):
        formatter_type = 'date'
        self.assertEqual(get_formatter_from_type(formatter_type), date_formatter)
        formatter_type = 'concat'
        self.assertEqual(get_formatter_from_type(formatter_type), concat_formatter)

    def test_duplicate_formatter(self):
        original_col_name = 'original'
        duplicate_col_name = 'duplicate'
        sample_dataframe = pd.DataFrame({original_col_name: [1, 2, 3, 5]})
        expected_dataframe = pd.DataFrame({
            original_col_name: sample_dataframe.original,
            duplicate_col_name: sample_dataframe.original
        })

        formatted_dataframe = duplicate_column_formatter(sample_dataframe, duplicate_col_name, original_col_name, {})

        pd.testing.assert_frame_equal(expected_dataframe, formatted_dataframe)

    @patch('ingen.formatters.common_formatters.log')
    def test_duplicate_formatter_with_missing_column(self, mock_logging):
        original_col_name = 'original'
        duplicate_col_name = 'duplicate'
        sample_dataframe = pd.DataFrame({original_col_name: [1, 2, 3, 5]})

        with self.assertRaises(KeyError):
            duplicate_column_formatter(sample_dataframe, duplicate_col_name, 'unknown column name', {})

        mock_logging.error.assert_called_with('Cannot create duplicate of a nonexistent column')

    def test_constant_string_formatter(self):
        sample_dataframe = pd.DataFrame({'col': [1, 2, 3, 4]})
        new_col_name = 'MY TEST COLUMN'
        const_string = 'test value'
        expected_dataframe = pd.DataFrame({
            'col': [1, 2, 3, 4],
            'MY TEST COLUMN': ['test value'] * 4
        })

        formatted_dataframe = constant_formatter(sample_dataframe, new_col_name, const_string, {})

        try:
            pd.testing.assert_frame_equal(expected_dataframe, formatted_dataframe)
        except AssertionError:
            self.fail('formatted dataframe is not equal to the expected dataframe')

    def test_empty_formatter(self):
        sample_dataframe = pd.DataFrame({'col': [1, 2, 3, 4]})
        new_col_name = 'MY TEST COLUMN'
        const_string = ''
        expected_dataframe = pd.DataFrame({
            'col': [1, 2, 3, 4],
            'MY TEST COLUMN': [''] * 4
        })

        formatted_dataframe = constant_formatter(sample_dataframe, new_col_name, const_string, {})

        try:
            pd.testing.assert_frame_equal(expected_dataframe, formatted_dataframe)
        except AssertionError:
            self.fail('formatted dataframe is not equal to the expected dataframe')

    def test_constant_date_formatter(self):
        sample_dataframe = pd.DataFrame({'col': [1, 2, 3, 4]})
        new_col_name = 'DATE'
        date_offset = 0
        date_format = '%m-%d-%y'
        calendar_country = 'US'
        format_options = [date_offset, date_format, calendar_country]
        today = date.today().strftime(date_format)
        expected_dataframe = pd.DataFrame({
            'col': sample_dataframe.col,
            new_col_name: [today] * 4
        })

        formatted_dataframe = constant_date_formatter(sample_dataframe, new_col_name, format_options, {})

        try:
            pd.testing.assert_frame_equal(expected_dataframe, formatted_dataframe)
        except AssertionError:
            self.fail('formatted dataframe is not equal to the expected dataframe')

    def test_constant_date_formatter_with_offset(self):
        sample_dataframe = pd.DataFrame({'col': [1, 2, 3, 4]})
        new_col_name = 'DATE'
        date_offset = -1
        date_format = '%m-%d-%y'
        calendar_type = 'IN'
        format_options = [date_offset, date_format, calendar_type]
        holiday_dict = holiday_calendar(country='IN')
        input_date = date.today() + timedelta(date_offset)
        while input_date in holiday_dict or input_date.weekday() > 4:
            input_date = input_date + timedelta(1)
        expected_dataframe = pd.DataFrame({
            'col': sample_dataframe.col,
            new_col_name: [input_date.strftime(date_format)] * 4
        })

        formatted_dataframe = constant_date_formatter(sample_dataframe, new_col_name, format_options, {})

        try:
            pd.testing.assert_frame_equal(expected_dataframe, formatted_dataframe)
        except AssertionError:
            self.fail('formatted dataframe is not equal to the expected dataframe')

    @patch('ingen.formatters.common_formatters.log')
    def test_missing_arguments_in_constant_date_formatter(self, mock_logging):
        sample_dataframe = pd.DataFrame({'col': [1, 2, 3, 4]})
        new_col_name = 'DATE'
        date_offset = -1
        date_format = '%m-%d-%y'
        format_options = [date_offset, date_format]
        expected_error_msg = 'Missing required formatting attributes for constant date formatter. It should be a ' \
                             'list of date_offset, date_format and calendar_country. e.g., [0, "%Y%m%d", "US"]'
        with self.assertRaises(ValueError):
            formatted_dataframe = constant_date_formatter(sample_dataframe, new_col_name, format_options, {})

        mock_logging.error.assert_called_with(expected_error_msg)

    def test_group_percentage_formatter(self):
        sample_data = pd.DataFrame({
            'portfolio': ['ABC', 'ABC', 'ABC', 'XYZ', 'XYZ', 'MNO'],
            'cusip': ['GOOGL', 'TSLA', 'APPL', 'GOOGL', 'MSFT', 'GOOGL'],
            'qty': [10, 15, 22, 10, 12, 20]
        })
        new_col_name = 'weight'
        param = {
            'of': 'qty',
            'in': 'portfolio'
        }
        cusip_weight_per_portfolio = [weight * 100 for weight in [10 / 47, 15 / 47, 22 / 47, 10 / 22, 12 / 22, 20 / 20]]

        expected_data = sample_data.copy()
        expected_data[new_col_name] = cusip_weight_per_portfolio

        formatted_data = group_percentage_formatter(sample_data, new_col_name, param, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    @patch('ingen.formatters.common_formatters.log')
    def test_group_percentage_with_missing_columns(self, mock_logging):
        sample_data = pd.DataFrame({
            'portfolio': ['ABC', 'ABC', 'ABC', 'XYZ', 'XYZ', 'MNO'],
            'cusip': ['GOOGL', 'TSLA', 'APPL', 'GOOGL', 'MSFT', 'GOOGL'],
            'qty': [10, 15, 22, 10, 12, 20]
        })
        new_col_name = 'weight'
        param = {
            'of': 'missing col',
            'in': 'portfolio'
        }

        with self.assertRaises(ValueError):
            group_percentage_formatter(sample_data, new_col_name, param, {})

        mock_logging.error.assert_called_with('Unknown column names provided for calculating grouped percentage.')

    def test_date_diff_formatter(self):
        sample_data = pd.DataFrame({
            'sell_date': ['', '2020-05-10', '2020-06-23'],
            'purchase_date': ['2020-04-14', '2020-04-14', '2020-05-19'],
            'qty': [10, 15, 22]
        })
        new_col_name = 'diff'
        format_options = ['sell_date', 'purchase_date', '%Y-%m-%d']

        diff_date_values = [np.nan, 26, 35]

        expected_data = sample_data.copy()
        expected_data[new_col_name] = diff_date_values

        formatted_data = date_diff_formatter(sample_data, new_col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_sum_value_formatter(self):
        sample_data = pd.DataFrame({
            'short_term_G_L': [0.0, 100.50, -300.45],
            'long_term_G_L': [100.90, 0.0, 0.0],
            'qty': [10, 15, 22]
        })
        new_col_name = 'sum'
        format_options = ['short_term_G_L', 'long_term_G_L']
        sum_values = [100.90, 100.50, -300.45]

        expected_data = sample_data.copy()
        expected_data[new_col_name] = sum_values

        formatted_data = sum_value_formatter(sample_data, new_col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_bucket_formatter(self):
        data = pd.DataFrame({
            'marks': [50, 90, 85, 75, 13]
        })

        format_options = {

            'buckets': [0, 40, 50, 60, 70, 80, 100],
            'labels': ['F', 'E', 'D', 'C', 'B', 'A']
        }
        expected_data = pd.DataFrame({
            'marks': ['E', 'A', 'A', 'B', 'F']
        })
        actual_data = bucket_formatter(data, 'marks', format_options, None)
        pd.testing.assert_frame_equal(expected_data, actual_data)

    def test_bucket_formatter_with_inf(self):
        data = pd.DataFrame({
            'GAIN_LOSS_TYPE': [-23, 0, 200, 366, 370, 400, 365]
        })
        format_options = {
            'buckets': ['-inf', -1, 365, 'inf'],
            'labels': ['invalid', 'short_term', 'long_term']
        }
        expected_data = pd.DataFrame({
            'GAIN_LOSS_TYPE': ['invalid', 'short_term', 'short_term', 'long_term', 'long_term', 'long_term',
                               'short_term']
        })
        actual_data = bucket_formatter(data, 'GAIN_LOSS_TYPE', format_options, None)
        pd.testing.assert_frame_equal(expected_data, actual_data)

    def test_mathematical_formatter_div(self):
        sample_data = pd.DataFrame({
            'price': [280, 585, 1100],
            'qty': [10, 15, 22]
        })
        col_name = 'weight'
        format_options = {
            'cols': ['price', 'qty'],
            'operation': 'div'
        }
        expected_data = sample_data.copy()
        expected_data[col_name] = [28.0, 39.0, 50.0]

        formatted_data = arithmetic_calculation_formatter(sample_data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_mathematical_formatter_mul(self):
        sample_data = pd.DataFrame({
            'weight': [28, 39, 50],
            'qty': [10, 15, 22]
        })
        col_name = 'price'
        format_options = {
            'cols': ['weight', 'qty'],
            'operation': 'mul'
        }

        expected_data = sample_data.copy()
        expected_data[col_name] = [280, 585, 1100]
        formatted_data = arithmetic_calculation_formatter(sample_data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_mathematical_formatter_add(self):
        sample_data = pd.DataFrame({
            'weight1': [28, 39, 50],
            'weight2': [10, 15, 22],
            'weight3': [12, 23, 27],
            'weight4': [56, 13, 22]
        })
        col_name = 'sum'
        format_options = {
            'cols': ['weight1', 'weight2', 'weight3', 'weight4'],
            'operation': 'add'
        }
        expected_data = sample_data.copy()
        expected_data[col_name] = [106, 90, 121]

        formatted_data = arithmetic_calculation_formatter(sample_data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_mathematical_formatter_div_with_just_value(self):
        sample_data = pd.DataFrame({
            'weight': [28, 39, 50],
            'qty': [10, 15, 22]
        })
        col_name = 'weight'
        format_options = {
            'value': 100,
            'operation': 'div'
        }
        expected_data = sample_data.copy()
        expected_data[col_name] = [0.28, .39, .50]

        formatted_data = arithmetic_calculation_formatter(sample_data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_mathematical_formatter_mul_with_just_value(self):
        sample_data = pd.DataFrame({
            'weight': [28, 39, 50],
            'qty': [10, 15, 22]
        })
        col_name = 'weight'
        format_options = {
            'value': 100,
            'operation': 'mul'
        }

        expected_data = sample_data.copy()
        expected_data[col_name] = [2800, 3900, 5000]
        formatted_data = arithmetic_calculation_formatter(sample_data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_mathematical_formatter_add_with_just_value(self):
        sample_data = pd.DataFrame({
            'weight': [28, 39, 50],
            'qty': [10, 15, 22]
        })
        col_name = 'weight'
        format_options = {
            'value': 100,
            'operation': 'add'
        }
        expected_data = sample_data.copy()
        expected_data[col_name] = [128, 139, 150]

        formatted_data = arithmetic_calculation_formatter(sample_data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_mathematical_formatter_subtract(self):
        sample_data = pd.DataFrame({
            'weight1': [28, 39, 50],
            'weight2': [10, 19, 20],
            'weight3': [6, 5, 10],
            'weight4': [2, 5, 10]
        })
        col_name = 'sub'
        format_options = {
            'cols': ['weight1', 'weight2', 'weight3', 'weight4'],
            'operation': 'sub',
            'value': 4
        }
        expected_data = sample_data.copy()
        expected_data[col_name] = [6, 6, 6]

        formatted_data = arithmetic_calculation_formatter(sample_data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_mathematical_formatter_abs(self):
        sample_data = pd.DataFrame({
            'weight': [-28, -39, -50]
        })
        col_name = 'weight'
        format_options = {
            'operation': 'abs'
        }

        expected_data = sample_data.copy()
        expected_data[col_name] = [28, 39, 50]
        formatted_data = arithmetic_calculation_formatter(sample_data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_fill_empty_values(self):
        data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', np.NaN, 'Mumbai'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune']
        })
        expected_data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', 'Kolkata', 'Mumbai'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune']
        })
        col_name = 'vacation_city'
        format_options = {
            'column': 'default_city'
        }
        formatted_data = fill_empty_values(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_fill_empty_values_missing_column(self):
        data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', np.NaN, 'Mumbai'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune']
        })
        col_name = 'vacation_city'
        format_options = {
            'column': 'missing_column'
        }

        with self.assertRaisesRegex(KeyError, f"Column '{format_options['column']}' not found."):
            fill_empty_values(data, col_name, format_options, {})

    def test_fill_empty_values_with_single_column(self):
        data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', np.NaN, 'Mumbai'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune']
        })
        expected_data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', 'xyz', 'Mumbai'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune']
        })
        col_name = 'vacation_city'
        format_options = {
            'value': 'xyz'
        }
        formatted_data = fill_empty_values_with_custom_value(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    @patch('ingen.formatters.common_formatters.log')
    def test_fill_empty_values_with_single_column_when_col_not_available(self, mock_logging):
        data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', np.NaN, 'Mumbai'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune']
        })

        col_name = 'abc'
        format_options = {
            'value': 'xyz'
        }

        with self.assertRaisesRegex(KeyError, f"Column '{col_name}' not found."):
            fill_empty_values_with_custom_value(data, col_name, format_options, {})

    def test_business_day_formatter(self):
        sample_data = pd.DataFrame({'date': ['30/05/2022', '02/05/2022', '03/05/2022', '04/05/2022']})
        sample_data['date'] = pd.to_datetime(sample_data['date'], format='%d/%m/%Y')

        new_col_name = 'billing_date'
        format_options = {
            'col': 'date',
            'format': '%d/%m/%Y',
            'cal': 'UnitedStates'
        }
        billing_date_val = ['27/05/2022', '02/05/2022', '03/05/2022', '04/05/2022']

        expected_data = sample_data.copy()
        expected_data[new_col_name] = pd.to_datetime(billing_date_val, format='%d/%m/%Y')

        formatted_data = business_day_formatter(sample_data, new_col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data, check_dtype=False)

    def test_replace_formatter(self):
        data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', 'abc', 'Mumbai'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune']
        })
        expected_data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', 'xyz', 'Mumbai'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune']
        })
        col_name = 'vacation_city'
        format_options = {
            'from_value': ['abc'],
            'to_value': ['xyz']
        }
        formatted_data = replace_value(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_replace_formatter_with_mutliple_values(self):
        data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', 'abc', 'Mumbai'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune']
        })
        expected_data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', 'xyz', 'Delhi'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune']
        })
        col_name = 'vacation_city'
        format_options = {
            'from_value': ['abc', 'Mumbai'],
            'to_value': ['xyz', 'Delhi']
        }
        formatted_data = replace_value(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_replace_formatter_with_missing_column(self):
        data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', '', 'Mumbai'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune']
        })
        col_name = 'some_column'
        format_options = {
            'from_value': ['abc'],
            'to_value': ['xyz']
        }

        with self.assertRaisesRegex(KeyError, f"Column '{col_name}' not found."):
            replace_value(data, col_name, format_options, {})

    def test_runtime_date_formatter(self):
        data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', 'abc', 'Mumbai'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune']
        })
        expected_data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', 'abc', 'Mumbai'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune'],
            'run_date': ['2021-09-12', '2021-09-12', '2021-09-12', '2021-09-12', '2021-09-12']
        })
        col_name = 'run_date'
        format_options = {
            'des': '%Y-%m-%d'
        }
        formatted_data = runtime_date(data, col_name, format_options, {'run_date': '09122021'})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_runtime_date_formatter_with_string_param(self):
        data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', 'abc', 'Mumbai'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune']
        })
        col_name = 'run_date'
        format_options = {
            'des': '%Y-%m-%d'
        }

        with self.assertRaises(ValueError):
            runtime_date(data, col_name, format_options, {'run_date': 'hello'})

    def test_fill_empty_values_with_condition(self):
        data = pd.DataFrame({
            'sec_desc': ['CASH', 'ATLANTA', 'CLARK',
                         'CASH', 'HONOLULU'],
            'purchase_date': [np.NaN, '11142019', '06052015', '04252019', np.NaN]
        })
        expected_data = pd.DataFrame({
            'sec_desc': ['CASH', 'ATLANTA', 'CLARK',
                         'CASH', 'HONOLULU'],
            'purchase_date': ['09102019', '11142019', '06052015', '04252019', np.NaN]
        })
        col_name = 'purchase_date'
        format_options = {
            'value': '09102019',
            'condition': {'match_col': 'sec_desc', 'pattern': 'CASH'}
        }
        formatted_data = fill_empty_values_with_custom_value(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_conditional_replace_formatter(self):
        data = pd.DataFrame({
            'SHARE': [123.00, 234.00, 567.00, 984.00, 89.00],
            'TRADE TYPE': ['BUY', 'SELL', 'SELL', 'BUY', 'BUY'],
            'PRICE': [20.00, 60.00, 10.00, 90.00, 80.00]
        })
        expected_data = pd.DataFrame({
            'SHARE': [123.00, 60.00, 10.00, 984.00, 89.00],
            'TRADE TYPE': ['BUY', 'SELL', 'SELL', 'BUY', 'BUY'],
            'PRICE': [20.00, 60.00, 10.00, 90.00, 80.00]
        })
        col_name = 'SHARE'
        format_options = {
            'from_column': 'PRICE',
            'condition': {'match_col': 'TRADE TYPE', 'pattern': 'SELL'}
        }

        formatted_data = conditional_replace_formatter(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_conditional_replace_formatter_for_numeric_column(self):
        data = pd.DataFrame({
            'SHARE': [123.00, 234.00, 567.00, 984.00, 89.00],
            'TRADE TYPE': [1, 1, 2, 2, 2],
            'PRICE': [20.00, 60.00, 10.00, 90.00, 80.00]
        })
        expected_data = pd.DataFrame({
            'SHARE': [20.00, 60.00, 567.00, 984.00, 89.00],
            'TRADE TYPE': [1, 1, 2, 2, 2],
            'PRICE': [20.00, 60.00, 10.00, 90.00, 80.00]
        })
        col_name = 'SHARE'
        format_options = {
            'from_column': 'PRICE',
            'condition': {'match_col': 'TRADE TYPE', 'pattern': 1}
        }

        formatted_data = conditional_replace_formatter(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    @patch('ingen.formatters.common_formatters.log')
    def test_conditional_replace_formatter_when_col_not_available(self, mock_logging):
        data = pd.DataFrame({
            'name': ['Angela', 'Mathews', 'Chris', 'Jade', 'Rohit'],
            'vacation_city': ['New York', 'Sydney', 'Perth', np.NaN, 'Mumbai'],
            'default_city': ['New York', 'Manhattan', 'Jerusalem', 'Kolkata', 'Pune']
        })

        col_name = 'abc'
        format_options = {
            'from_column': 'PRICE',
            'condition': {'match_col': 'TRADE TYPE', 'pattern': 'SELL'}
        }

        with self.assertRaisesRegex(KeyError, f"Column '{col_name}' not found."):
            fill_empty_values_with_custom_value(data, col_name, format_options, {})

    def test_uuid_formatter(self):
        col_length = 50000
        data = pd.DataFrame({
            'col1': ['value1'] * col_length,
            'col2': ['value2'] * col_length
        })
        new_col_name = 'uuid'
        start = time.time()
        actual_data = add_uuid_col(data, new_col_name, None, None)
        end = time.time()
        print(f"UUID generation took {end - start:.2f} seconds.")
        self.assertIsNotNone(actual_data[new_col_name])
        self.assertEqual(len(actual_data[new_col_name]), col_length)
        self.assertIsInstance(data[new_col_name][0], uuid.UUID)

    def test_extract_from_pattern(self):
        data = pd.DataFrame({
            'FA Contact': ['704-871-5645 name@org.com', '212-284-5896', '', ' name@org.com'],
        })
        expected_data = pd.DataFrame({
            'FA Contact': ['name@org.com', None, None, 'name@org.com'],
        })

        col_name = 'FA Contact'

        format_options = {
            'pattern': r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+'
        }

        values = extract_from_pattern(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, values)

    def test_index_counter(self):
        data = pd.DataFrame({
            'FA Contact': ['abc', 'def', 'hij'],
        })
        expected_data = pd.DataFrame({
            'FA Contact': [0, 1, 2],
        })

        col_name = 'FA Contact'

        indexed_dataframe = index_counter(data, col_name, {}, {})
        pd.testing.assert_frame_equal(expected_data, indexed_dataframe)

    def test_get_timestamp(self):
        data = pd.DataFrame({
            'current_timestamp': ['test1', 'test2', 'test3'],
        })

        ts = calendar.timegm(time.gmtime())

        expected_data = pd.DataFrame({
            'current_timestamp': [ts, ts, ts],
        })

        col_name = 'current_timestamp'

        indexed_dataframe = current_timestamp(data, col_name, {}, {})
        pd.testing.assert_frame_equal(expected_data, indexed_dataframe)

    @patch('ingen.formatters.common_formatters.Properties')
    def test_get_running_environment(self, mock_properties):
        mock_properties.get_property.return_value = 'DEV'
        data = pd.DataFrame({
            'External_Id': ['test1', 'test2', 'test3'],
        })
        expected_data = pd.DataFrame({
            'External_Id': ['7863816313', '7863816313', '7863816313'],
        })

        col_name = 'External_Id'

        format_options = {
            'DEV': '7863816313',
            'TST': '7863816313',
            'PROD': '7863816313'
        }

        indexed_dataframe = get_running_environment(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, indexed_dataframe)

    def test_sub_string(self):
        data = pd.DataFrame({
            'ACCOUNT_ID': ['Z88262400', 'Z88262410', 'Z88262420', 'Z88262430', 'Z88262440'],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        expected_data = pd.DataFrame({
            'ACCOUNT_ID': ['88262400', '88262410', '88262420', '88262430', '88262440'],
            'CUSIP': ['092480201', '092480203', '122480201', '242480201', '372480201']
        })
        col_name = 'ACCOUNT_ID'
        format_options = {
            'start': 1
        }
        formatted_data = sub_string(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_sub_string_with_optional_indices(self):
        data = pd.DataFrame({
            'column': [2090.2, 901.1, 800.0]
        })
        expected_data = pd.DataFrame({
            'column': ['2090', '901', '800']
        })
        col_name = 'column'
        format_options = {
            'end': -2
        }
        formatted_data = sub_string(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_float_precision(self):
        data = pd.DataFrame({
            'numbers': [2.23223, 2.7777777, 34.3333332, 44.3434345, 77.3343434322, 112.9833],
        })
        expected_data = pd.DataFrame({
            'numbers': [2.23, 2.78, 34.33, 44.34, 77.33, 112.98]
        })
        col_name = 'numbers'
        format_options = {
            'precision': 2
        }
        formatted_data = float_precision(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_float_precision_throws_error_on_string_col(self):
        data = pd.DataFrame({
            'numbers': ['2.23223', 2.7777777, 34.3333332, 44.3434345, 77.3343434322],
        })
        col_name = 'numbers'
        format_options = {
            'precision': 2
        }
        with self.assertRaises(TypeError):
            float_precision(data, col_name, format_options, {})

    def test_drop_duplicates_default(self):
        data = pd.DataFrame({
            'ID': ['39VN39GJ3', '4MGFK4249', '4MGFK4249', '4MGFK4249'],
            'NAME': ['Russell', 'Carlyle', 'Ronya', 'Angela'],
            'ACCOUNT': ['10270012', '59375304', '85910683', '02759175']
        })
        expected_data = pd.DataFrame({
            'ID': ['39VN39GJ3', '4MGFK4249'],
            'NAME': ['Russell', 'Carlyle'],
            'ACCOUNT': ['10270012', '59375304']
        })
        col_name = 'ID'
        format_options = {}
        formatted_data = drop_duplicates(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_drop_duplicates_first(self):
        data = pd.DataFrame({
            'ID': ['39VN39GJ3', '4MGFK4249', '4MGFK4249', '4MGFK4249'],
            'NAME': ['Russell', 'Carlyle', 'Ronya', 'Angela'],
            'ACCOUNT': ['10270012', '59375304', '85910683', '02759175']
        })
        expected_data = pd.DataFrame({
            'ID': ['39VN39GJ3', '4MGFK4249'],
            'NAME': ['Russell', 'Carlyle'],
            'ACCOUNT': ['10270012', '59375304']
        })
        col_name = 'ID'
        format_options = {
            'keep': 'first'
        }
        formatted_data = drop_duplicates(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_drop_duplicates_last(self):
        data = pd.DataFrame({
            'ID': ['39VN39GJ3', '4MGFK4249', '4MGFK4249', '4MGFK4249'],
            'NAME': ['Russell', 'Carlyle', 'Ronya', 'Angela'],
            'ACCOUNT': ['10270012', '59375304', '85910683', '02759175']
        })
        expected_data = data.drop([1, 2])
        col_name = 'ID'
        format_options = {
            'keep': 'last'
        }
        formatted_data = drop_duplicates(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_drop_duplicates_all(self):
        data = pd.DataFrame({
            'ID': ['39VN39GJ3', '4MGFK4249', '4MGFK4249', '4MGFK4249'],
            'NAME': ['Russell', 'Carlyle', 'Ronya', 'Angela'],
            'ACCOUNT': ['10270012', '59375304', '85910683', '02759175']
        })
        expected_data = pd.DataFrame({
            'ID': ['39VN39GJ3'],
            'NAME': ['Russell'],
            'ACCOUNT': ['10270012']
        })
        col_name = 'ID'
        format_options = {
            'keep': False
        }
        formatted_data = drop_duplicates(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def test_drop_duplicates_invalid_keep(self):
        data = pd.DataFrame({
            'ID': ['39VN39GJ3', '4MGFK4249', '4MGFK4249', '4MGFK4249'],
            'NAME': ['Russell', 'Carlyle', 'Ronya', 'Angela'],
            'ACCOUNT': ['10270012', '59375304', '85910683', '02759175']
        })
        expected_data = pd.DataFrame({
            'ID': ['39VN39GJ3', '4MGFK4249'],
            'NAME': ['Russell', 'Carlyle'],
            'ACCOUNT': ['10270012', '59375304']
        })
        col_name = 'ID'
        format_options = {
            'keep': 'all'
        }
        formatted_data = drop_duplicates(data, col_name, format_options, {})
        pd.testing.assert_frame_equal(expected_data, formatted_data)

    def custom_formatter(config, data):
        return data

    def test_add_formatter(self):
        formatter_type = 'cust'
        custom_formatter_func = self.custom_formatter
        add_formatter(formatter_type, custom_formatter_func)

        self.assertEqual(get_formatter_from_type(formatter_type), custom_formatter_func)

    def test_suffix_string_formatter(self):
        df = pd.DataFrame({
            "candidate": ["Harry", "Luna", "Draco", "Cedric"],
            "house": ["Gryffindor", "Ravenclaw", "Slytherin", "Hufflepuff"],

        })
        output_column = 'ID'
        input_columns = ['candidate', 'house']
        param = {
            'columns': input_columns,
            'suffix': '_WZD',
            'separator': '_'
        }
        expected_output_column = pd.Series(
            ["Harry_Gryffindor_WZD", "Luna_Ravenclaw_WZD", "Draco_Slytherin_WZD", "Cedric_Hufflepuff_WZD"])
        suffix_string_formatter(df, output_column, param, {})
        self.assertTrue(pd.Series.equals(df['ID'], expected_output_column))

    def test_constant_condition_formatter_basic(self):
        df = pd.DataFrame({
            'status': ['active', 'inactive', 'active', 'pending']
        })
        config = {
            'match_col': 'status',
            'compare': ['==', 'active'],
            'values': ['YES', 'NO']
        }
        result = constant_condition_formatter(df, 'is_active', config, None)
        expected = pd.Series(['YES', 'NO', 'YES', 'NO'], name='is_active')
        pd.testing.assert_series_equal(result['is_active'], expected)

    def test_constant_condition_formatter_single_value(self):
        df = pd.DataFrame({
            'amount': [100, 200, 300, 400],
            'status': ['active', 'inactive', 'active', 'pending']
        })
        config = {
            'match_col': 'status',
            'compare': ['==', 'active'],
            'values': [1000]  # Only one value provided
        }
        result = constant_condition_formatter(df, 'amount', config, None)
        expected = pd.Series([1000, 200, 1000, 400], name='amount')
        pd.testing.assert_series_equal(result['amount'], expected)

    def test_constant_condition_formatter_match_override_skip(self):
        df = pd.DataFrame({
            'status': ['active', 'inactive']
        })
        config = {
            'match_override': 'type',
            'pattern': 'skip_me',
            'match_col': 'status',
            'compare': ['==', 'active'],
            'values': ['YES', 'NO']
        }
        runtime_params = {
            'override_params': {
                'type': 'skip_me'  # This matches the pattern, so formatter should skip
            }
        }
        result = constant_condition_formatter(df.copy(), 'is_active', config, runtime_params)
        pd.testing.assert_frame_equal(result, df)  # Should be unchanged

    def test_constant_condition_formatter_match_override_no_skip(self):
        df = pd.DataFrame({
            'status': ['active', 'inactive']
        })
        config = {
            'condition': {
                'match_override': 'type',
                'pattern': 'skip_me'
            },
            'match_col': 'status',
            'compare': ['==', 'active'],
            'values': ['YES', 'NO']
        }
        runtime_params = {
            'override_params': {
                'type': 'process_me'  # Doesn't match pattern, so formatter should run
            }
        }
        result = constant_condition_formatter(df, 'is_active', config, runtime_params)
        expected = pd.Series(['YES', 'NO'], name='is_active')
        pd.testing.assert_series_equal(result['is_active'], expected)

    def test_override_formatter_with_valid_params(self):
        df = pd.DataFrame({'A': [1, 2, 3]})
        runtime_params = {
            'override_params': {
                'test_key': 'test_value',
                'other_key': 'other_value'
            }
        }
        result = override_formatter(df.copy(), 'A', 'test_key', runtime_params)
        expected = pd.Series(['test_value'] * 3, name='A')
        pd.testing.assert_series_equal(result['A'], expected)

    def test_override_formatter_with_missing_key(self):
        df = pd.DataFrame({'A': [1, 2, 3]})
        runtime_params = {
            'override_params': {
                'other_key': 'other_value'
            }
        }
        result = override_formatter(df.copy(), 'A', 'non_existent_key', runtime_params)
        pd.testing.assert_series_equal(result['A'], pd.Series([None, None, None], dtype=object, name='A'))

if __name__ == '__main__':
    unittest.main()
