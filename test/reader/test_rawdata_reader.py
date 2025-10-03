#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pytest
import pandas as pd

from ingen.data_source.dataframe_store import store
from ingen.reader.rawdata_reader import RawDataReader


class TestRawDataReader:
    
    def test_get_frame_id(self, monkeypatch):
        test_store = {'contact': pd.DataFrame({
            'First': ['sam', 'some', 'neha'],
            'gender': ['F', 'M', 'F']
        })}
        
        monkeypatch.setattr("ingen.data_source.dataframe_store.store", test_store)
        
        _id = 'contact'
        expected_dataframe = pd.DataFrame(
            {
                'First': ['sam', 'some', 'neha'],
                'gender': ['F', 'M', 'F']
            })

        reader = RawDataReader()
        data = reader.read(_id, test_store)
        pd.testing.assert_frame_equal(expected_dataframe.sort_index(axis=1),
                                      data.sort_index(axis=1))

    def test_get_frame_id_wrong_id(self):
        _id = "height"
        with pytest.raises(KeyError, match="'height'"):
            reader = RawDataReader()
            data = reader.read(_id, store)