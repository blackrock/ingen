import unittest
from pathlib import Path
from pyexpat import ExpatError
from typing import Dict, Union, List
from unittest.mock import patch

import pandas as pd

from ingen.reader.xml_file_reader import XMLFileReader

THIS_DIR = Path(__file__).parent


class TestXMLFileReader(unittest.TestCase):
    def setUp(self):
        self.xml_src = {
            'id': 'order_xml',
            'type': 'file',
            'file_type': 'xml',
            'file_path': f'{THIS_DIR.parent}/input/test.xml',
            'columns': [
                'ORDER_ID',
                'ORD_DETAIL_set.ORD_DETAIL.ITEM_NAME',
                'ORD_DETAIL_set.ORD_DETAIL.QUANTITY',
                'ASSIGNED_TO.@id'
            ],
            'root_tag': 'ORDER'
        }
        self.xml_nested_src = {
            'id': 'order_xml',
            'type': 'file',
            'file_type': 'xml',
            'file_path': f'{THIS_DIR.parent}/input/orders.xml',
            'columns': [
                'ORDER_ID',
                'CURRENCY',
                'ORD_DETAIL_set.ORD_DETAIL.ITEM_NAME'
            ],
            'root_tag': 'ORDER'
        }
        self.xml_src_with_one_record = {
            'id': 'order_xml',
            'type': 'file',
            'file_type': 'xml',
            'file_path': f'{THIS_DIR.parent}/input/test2.xml',
            'columns': [
                'ORDER_ID',
                'ORD_DETAIL_set.ORD_DETAIL.ITEM_NAME',
                'ORD_DETAIL_set.ORD_DETAIL.QUANTITY'
            ],
            'root_tag': 'ORDER'
        }
        self.xml_src_with_zero_record = {
            'id': 'order_xml',
            'type': 'file',
            'file_type': 'xml',
            'file_path': f'{THIS_DIR.parent}/input/test_zero.xml',
            'columns': [
                'ORDER_ID',
                'ORD_DETAIL_set.ORD_DETAIL.ITEM_NAME',
                'ORD_DETAIL_set.ORD_DETAIL.QUANTITY'
            ],
            'root_tag': 'ORDER'
        }
        self.xml_empty = {
            'id': 'xml_empty',
            'type': 'file',
            'file_type': 'xml',
            'file_path': f'{THIS_DIR.parent}/input/test_empty.xml',
            'columns': [
                'ORDER_ID',
                'ORD_DETAIL_set.ORD_DETAIL.ITEM_NAME',
                'ORD_DETAIL_set.ORD_DETAIL.QUANTITY'
            ],
            'root_tag': 'ORDER'
        }

    def test_xml(self):
        source = self.xml_src

        reader = XMLFileReader()
        data = reader.read(source)
        keys = {'ORDER_ID': ['0924802', '0924803'],
                'ORD_DETAIL_set.ORD_DETAIL.ITEM_NAME': ['Bread', 'Milk'],
                'ORD_DETAIL_set.ORD_DETAIL.QUANTITY': ['2', '1'],
                'ASSIGNED_TO.@id': ['', '1']}
        expected_data = pd.DataFrame(keys,
                                     columns=source['columns'])
        pd.testing.assert_frame_equal(expected_data, data)

    def test_xml_for_one_record(self):
        source = self.xml_src_with_one_record
        reader = XMLFileReader()
        data = reader.read(source)
        keys = {'ORDER_ID': ['0924806', '0924806'],
                'ORD_DETAIL_set.ORD_DETAIL.ITEM_NAME': ['Milk', 'Bread'],
                'ORD_DETAIL_set.ORD_DETAIL.QUANTITY': ['1', '2']}
        expected_data = pd.DataFrame(keys,
                                     columns=source['columns'])
        pd.testing.assert_frame_equal(expected_data, data)

    def test_xml_for_zero_record(self):
        source = self.xml_src_with_zero_record
        reader = XMLFileReader()
        data = reader.read(source)
        keys = {}
        expected_data = pd.DataFrame(keys,
                                     columns=source['columns'])
        pd.testing.assert_frame_equal(expected_data, data)

    def test_nested_xml(self):
        source = self.xml_nested_src

        expected_data = pd.DataFrame({
            'ORDER_ID': ['9248050', '9248020', '9248020', '9248060'],
            'CURRENCY': ['USD'] * 4,
            'ORD_DETAIL_set.ORD_DETAIL.ITEM_NAME': ['Bread', 'Milk', 'Coke', 'Detergent']
        })

        reader = XMLFileReader()
        data = reader.read(source)
        pd.testing.assert_frame_equal(expected_data, data)

    @patch('ingen.reader.xml_file_reader.logging')
    def test_empty_xml_file(self, mock_logging):
        source = self.xml_empty
        reader = XMLFileReader()
        with self.assertRaises(ExpatError):
            reader.read(source)
            error_msg = "XML file is empty"
            mock_logging.error.assert_called_with(error_msg)


if __name__ == '__main__':
    unittest.main()
