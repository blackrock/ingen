#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from ingen.reader.file_reader import ReaderFactory


class TestJsonReader(unittest.TestCase):
    def setUp(self):
        self.json_src = {
            'id': 'proposals',
            'type': 'file',
            'file_type': 'json',
            'file_path': './test/input/test_json.json',
            'record_path': 'positions',
            'meta': ["id", "cash_allocation"],
            'meta_prefix': 'position'
        }

        self._src_meta_prefix_none = {
            'id': 'proposals',
            'type': 'file',
            'file_type': 'json',
            'file_path': './test/input/test_json1.json',
            'record_path': 'positions',
            'meta': ["name", "cash_allocation"],
            'meta_prefix': None
        }

        self._src_meta_none = {
            'id': 'proposals',
            'type': 'file',
            'file_type': 'json',
            'file_path': './test/input/test_json.json',
            'record_path': 'positions',
            'meta': None,
            'meta_prefix': 'position'
        }

        self._src_record_path_none = {
            'id': 'proposals',
            'type': 'file',
            'file_type': 'json',
            'file_path': './test/input/test_json2.json',
            'record_path': None,
        }

    def test_read(self):
        source = self.json_src
        reader = ReaderFactory.get_reader(source)
        data = reader.read(source)

        expected_data = pd.DataFrame(
            {'id': ['88877701000000BLANK'], 'cusip': ['USD0000'], 'marketValue': [6920.2], 'quantity': [6920.2],
             'posInfo.client_id': ['000000BLANK'], 'posInfo.pos_id': ['88877701000000BLANK'],
             'posInfo.SLEEVE_ID': ['ABC'],
             'positionid': ['proposal_id_111'], 'positioncash_allocation': [20000]})
        assert_frame_equal(data, expected_data, check_dtype=False)

    def test_meta_prefix_none(self):
        source = self._src_meta_prefix_none
        reader = ReaderFactory.get_reader(source)
        data = reader.read(source)
        print(data)
        expected_data = pd.DataFrame(
            {'id': ['88877701000000BLANK'], 'cusip': ['USD0000'], 'marketValue': [6920.2], 'quantity': [6920.2],
             'posInfo.client_id': ['000000BLANK'], 'posInfo.pos_id': ['88877701000000BLANK'],
             'posInfo.SLEEVE_ID': ['ABC'],
             'name': ['proposal_id_111'], 'cash_allocation': [20000]})
        assert_frame_equal(data, expected_data, check_dtype=False)

    def test_meta_none(self):
        source = self._src_meta_none
        reader = ReaderFactory.get_reader(source)
        data = reader.read(source)
        expected_data = pd.DataFrame(
            {'id': ['88877701000000BLANK'], 'cusip': ['USD0000'], 'marketValue': [6920.2], 'quantity': [6920.2],
             'posInfo.client_id': ['000000BLANK'], 'posInfo.pos_id': ['88877701000000BLANK'],
             'posInfo.SLEEVE_ID': ['ABC']})
        assert_frame_equal(data, expected_data, check_dtype=False)

    def test_record_path_none(self):
        source = self._src_record_path_none
        reader = ReaderFactory.get_reader(source)
        data = reader.read(source)
        expected_data = pd.DataFrame(
            {'name': ['proposal_id_111'], 'cash_allocation': [20000], 'id': ['88877701000000BLANK'],
             'cusip': ['USD0000'], 'marketValue': [6920.2], 'quantity': [6920.2]})
        assert_frame_equal(data, expected_data, check_dtype=False)


if __name__ == '__main__':
    unittest.main()
