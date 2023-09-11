#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import re


class DFToMultipleJsonConvertor:
    def convert(self, df, convertor_props):
        json_template = convertor_props.get('json_template')
        json_strings = []
        for i, r in df.iterrows():
            json_strings.append(re.sub('<(.*?)>', lambda match, row=r: str(row[match.group()[1:-1]]), json_template))
        return json_strings
