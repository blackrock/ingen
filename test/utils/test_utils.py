import argparse
import unittest

from ingen.utils.utils import KeyValue


class MyTestCase(unittest.TestCase):
    def test_command_line_key_value_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--query_params', nargs='*', action=KeyValue)
        args = parser.parse_args(['--query_params', 'date=12/09/1995', 'table=position'])
        self.assertDictEqual({'date': '12/09/1995', 'table': 'position'}, args.query_params)
        return parser


if __name__ == '__main__':
    unittest.main()
