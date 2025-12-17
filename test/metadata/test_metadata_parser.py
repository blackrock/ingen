#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import os
import unittest
from datetime import date
from unittest.mock import patch, MagicMock

from ingen.metadata.metadata_parser import MetaDataParser


class TestMetaDataParser(unittest.TestCase):
    def setUp(self):
        script_dir = os.path.dirname(__file__)
        config_file_path = "../input/pos-ret.yml"
        required_interfaces = ["account"]
        run_date = date.today()
        override_params = {'key1': 'value1', 'key2': 'value2'}
        self.parser_for_filtered_interfaces = MetaDataParser(
            os.path.join(script_dir, config_file_path),
            {"date": "12/09/1995"},
            run_date,
            required_interfaces,
            override_params=override_params
        )
        certain_interfaces_list = ["positions", "account", "tax-lots"]
        self.parser_for_certain_interfaces = MetaDataParser(
            os.path.join(script_dir, config_file_path),
            {"date": "12/09/1995"},
            run_date,
            certain_interfaces_list,
        )

        self.filtered_interfaces = self.parser_for_filtered_interfaces.parse_metadata()
        self.certain_interfaces = self.parser_for_certain_interfaces.parse_metadata()
        self.parser = MetaDataParser(
            os.path.join(script_dir, config_file_path),
            {"date": "12/09/1995"},
            run_date,
            None,
        )
        self.interfaces = self.parser.parse_metadata()

    # this scenario checks when interface_list ia not provided, here all the interfaces present in our
    # interface metadata ('account' , 'positions') 2 will be fetched.
    def test_parse_config_reads_all_interfaces(self):
        self.assertTrue(len(self.interfaces) == 2)

    # this scenario checks when interface provided in the interface_list is present in our interface metadata-
    # here only 'account' is being fetched, although 'positions' is also  present in interface metadata
    def test_parse_config_reads_required_interfaces(self):
        self.assertTrue(len(self.filtered_interfaces) == 1)

    # this scenario checks when interface provided in the interface_list is not present in our interface metadata-
    # here tax-lots is not present in interface metadata, only 'positions', 'account' will ne fetched
    def test_parse_config_reads_certain_interfaces(self):
        self.assertTrue(len(self.certain_interfaces) == 2)


if __name__ == "__main__":
    unittest.main()
