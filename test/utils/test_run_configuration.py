#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from unittest.mock import patch

from ingen.formatters.formatter import Formatter
from ingen.generators.interface_generator import InterfaceGenerator
from ingen.utils.run_configuration import RunConfiguration
from ingen.writer.writer import InterfaceWriter


class TestClass:
    pass


class MyTestCase(unittest.TestCase):
    def setUp(self):
        config = {
            'formatter': 'CustomFormatter',
            'writer': 'CustomWriter',
            'generator': 'CustomGenerator'
        }
        self.config = RunConfiguration(config)

    @patch('ingen.utils.run_configuration.generators')
    def test_generator(self, mock_generators):
        setattr(mock_generators, 'CustomGenerator', TestClass)
        self.assertEqual(TestClass, self.config.generator)

    @patch('ingen.utils.run_configuration.formatters')
    def test_formatter(self, mock_formatters):
        setattr(mock_formatters, 'CustomFormatter', TestClass)
        self.assertEqual(TestClass, self.config.formatter)

    @patch('ingen.utils.run_configuration.writers')
    def test_writer(self, mock_writers):
        setattr(mock_writers, 'CustomWriter', TestClass)
        self.assertEqual(TestClass, self.config.writer)

    def test_defaults(self):
        config = RunConfiguration({})
        self.assertEqual(InterfaceGenerator, config.generator)
        self.assertEqual(InterfaceWriter, config.writer)
        self.assertEqual(Formatter, config.formatter)


if __name__ == '__main__':
    unittest.main()
