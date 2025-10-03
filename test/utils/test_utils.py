#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import argparse

from ingen.utils.utils import KeyValue


class TestUtils:
    def test_command_line_key_value_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--query_params', nargs='*', action=KeyValue)
        args = parser.parse_args(['--query_params', 'date=12/09/1995', 'table=position'])
        assert args.query_params == {'date': '12/09/1995', 'table': 'position'}
