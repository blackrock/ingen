#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from datetime import date

import pandas as pd

from ingen.writer import process_dataframe_columns_schema
from ingen.writer.json_util import json_sum


class TestJsonUtil:
    def test_dataframe_with_no_action(self):
        data = {'foo_id': [1, 2, 3], 'bar_id': ['alpha', 'beta', 'gamma']}
        df = pd.DataFrame(data=data)
        column_details = {'schema': [{'field_name': 'foo_id'}], 'resultant_columns': ['foo_id']}
        result_df = process_dataframe_columns_schema(df, column_details)
        assert df[['foo_id']].equals(result_df)

    def test_dataframe_with_dict_groupby(self):
        data = {'foo_id': [1, 2, 3], 'bar_id': ['alpha', 'beta', 'gamma'], 'product': ['particle', 'particle', 'boson']}
        df = pd.DataFrame(data=data)
        column_details = {'schema': [{'field_name': 'info', 'field_type': 'dict',
                                      'field_attr': ['foo_id', 'bar_id', ],
                                      'field_action': 'groupby', 'field_action_column': 'product',
                                      'field_agg_column': 'info'}
                                     ],
                          'resultant_columns': ['product', 'info']}

        result_df = process_dataframe_columns_schema(df, column_details)
        expected_df = pd.DataFrame(data={
            'product': ['boson', 'particle'],
            'info': [
                [{'foo_id': 3, 'bar_id': 'gamma'}],
                [
                    {'foo_id': 1, 'bar_id': 'alpha'},
                    {'foo_id': 2, 'bar_id': 'beta'}
                ]
            ]
        })
        assert expected_df.equals(result_df)

    def test_dataframe_with_date_col(self):
        data = {'foo_id': [1, 2, 3]}
        df = pd.DataFrame(data=data)
        column_details = {'schema': [{'field_name': 'asOfDate', 'field_type': 'date'}],
                          'resultant_columns': ['foo_id', 'asOfDate']}

        result_df = process_dataframe_columns_schema(df, column_details)
        expected_df = df.copy()
        expected_df['asOfDate'] = str(date.today())
        assert expected_df.equals(result_df)

    def test_dataframe_with_no_resultant_col(self):
        data = {'foo_id': [1, 2, 3]}
        df = pd.DataFrame(data=data)
        column_details = {'schema': [{'field_name': 'asOfDate', 'field_type': 'date'}]}

        result_df = process_dataframe_columns_schema(df, column_details)
        expected_df = pd.DataFrame(data)
        assert expected_df[[]].equals(result_df)

    def test_calculate_total_account_market_value(self):
        data = [{"advisorId": 4571638, "accounts": [
            {"accountName": "ABC", "accountNumber": "12345",
             "registrationType": "01 - INDIVIDUAL", "custodian": "CUST-1",
             "product": "Target Allocation Hybrid", "accountId": "88877701",
             "accountBaseMarketValue": 86817.93},
            {"accountName": "ABC", "accountNumber": "34345",
             "registrationType": "01 - INDIVIDUAL", "custodian": "CUST-1",
             "product": "Target Allocation Hybrid", "accountId": "88877701",
             "accountBaseMarketValue": 86817.93}], "asOfDate": "2022-06-06"}]
        dataframe = pd.DataFrame(data=data)
        schema = {'schema': [
            {'field_name': 'clientsSummary', 'field_type': 'dict', 'field_attr': ['asOfDate', 'accounts'],
             'field_action': 'sum', 'field_action_column': 'accountBaseMarketValue', 'field_agg_column': 'accounts',
             'field_total': 'totalAccountBaseMarketValue'}],
            'resultant_columns': ['advisorId', 'clientsSummary']}
        result_df = process_dataframe_columns_schema(dataframe, schema)
        assert 173635.86 == result_df.to_dict(orient='records')[0]['clientsSummary']['totalAccountBaseMarketValue']

    def test_sum_method_with_list_data(self):
        data = [123.23, 223.23, 444, 12]
        total = json_sum(obj=data)
        assert 802.46 == total

    def test_sum_method_with_single_d_hash(self):
        data = {'nums': [123.23, 223.23, 444, 12]}
        total = json_sum(obj=data, field='nums', result='totalSum')
        assert 802.46 == total['totalSum']

    def test_sum_method_with_two_d_hash(self):
        data = {'accs': [{'num': 23},
                         {'num': 23}]}
        total = json_sum(obj=data, field='accs', subfield='num', result='totalSum')
        assert 46.0 == total['totalSum']