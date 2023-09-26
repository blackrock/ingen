"""
This script convert json file to csv file
"""
#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import json

import pandas as pd


class JSONFileReader:

    def read(self, src):
        with open(src.get('file_path'), 'r') as res:
            data = json.load(res)
        df = pd.json_normalize(data, src.get('record_path'), src.get('meta'), src.get('meta_prefix'))
        return df
