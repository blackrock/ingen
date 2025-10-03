#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pytest
import pandas as pd
from pandas.testing import assert_frame_equal

from ingen.data_source.json_source import JsonSource


class TestJsonSource:
    def setup_method(self):
        self._src = {
            'id': 'json_string',
            'type': 'json'

        }
        self._data = """{
        "json_string": {
                "col1": "val1",
                "col2": "val2"
            }
        }"""
        self.source = JsonSource(self._src, self._data)

    def test_source_fetch(self):
        expected_df = pd.DataFrame({
            'col1': ['val1'],
            'col2': ['val2']
        })

        assert_frame_equal(expected_df, self.source.fetch())

    def test_source_fetch_empty_payload(self):
        self.source = JsonSource(self._src, "")
        with pytest.raises(ValueError):
            self.source.fetch()

    def test_source_fetch_malformed_payload(self):
        bad_payload = """{
                        'missing': 'end'
                    """
        self.source = JsonSource(self._src, bad_payload)
        with pytest.raises(ValueError):
            self.source.fetch()

    def test_source_fetch_validations(self):
        assert [] == self.source.fetch_validations()
