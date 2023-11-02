#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import json

import pandas as pd

from ingen.data_source.source import DataSource


class JsonSource(DataSource):

    def __init__(self, source, data):
        """
        Loads a JsonSource
        :param source: Map which contains source data such as id and data
        """

        super().__init__(source.get('id'))
        self._src = source
        self._data = data

    def fetch(self):
        if not self._data:
            raise ValueError("JSON string is not provided")

        json_dict = json.loads(self._data)
        if not json_dict[self.id]:
            raise ValueError("JSON source with ID {} does not exist".format(self.id))
        self._data = pd.json_normalize(json_dict[self.id])
        return self._data

    def fetch_validations(self):
        return self._src.get('src_data_checks', [])
