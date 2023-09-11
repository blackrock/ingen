#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest

import pandas as pd

from ingen.data_source.dataframe_store import store
from ingen.reader.rawdata_reader import RawDataReader
from ingen.writer.writer import *


class TestWriter(unittest.TestCase):

    def test_dataframewriter(self):
        expected_dataframe = pd.DataFrame(
            {
                'First': ['sam', 'some', 'neha'],
                'gender': ['F', 'M', 'F']
            })
        df = pd.DataFrame(
            {
                'First': ['sam', 'some', 'neha'],
                'gender': ['F', 'M', 'F']
            })
        props = {'id': 'contact'}
        writer = DataFrameWriter(df=df, writer_props=props)
        writer.write()
        pd.testing.assert_frame_equal(expected_dataframe, store.get(props.get('id')))

    def test_dataframewriter_with_reader(self):
        df = pd.DataFrame(
            {
                'First': ['sam', 'some', 'neha'],
                'gender': ['F', 'M', 'F']
            })
        props = {'id': 'contact'}
        writer = DataFrameWriter(df=df, writer_props=props)
        writer.write()
        reader = RawDataReader()
        data = reader.read(props.get('id'), store)
        pd.testing.assert_frame_equal(df, data)


if __name__ == '__main__':
    unittest.main()
