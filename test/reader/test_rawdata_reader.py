#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from unittest.mock import patch

import pandas as pd

from ingen.data_source.dataframe_store import store
from ingen.reader.rawdata_reader import RawDataReader


class TestRawDataReader(unittest.TestCase):
    @patch.dict(store, {'contact': pd.DataFrame({
        'First': ['sam', 'some', 'neha'],
        'gender': ['F', 'M', 'F']

    })
    })
    def testgetframeid(self):
        _id = 'contact'
        expected_dataframe = pd.DataFrame(
            {
                'First': ['sam', 'some', 'neha'],
                'gender': ['F', 'M', 'F']
            })

        reader = RawDataReader()
        data = reader.read(_id, store)
        pd.testing.assert_frame_equal(expected_dataframe.sort_index(axis=1),
                                      data.sort_index(axis=1))

    def testgetframeid_wrongid(self):
        _id = "height"
        with self.assertRaisesRegex(KeyError, "'height'"):
            reader = RawDataReader()
            data = reader.read(_id, store)
