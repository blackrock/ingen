#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pytest

from ingen.formatters.formatter import Formatter
from ingen.generators.interface_generator import InterfaceGenerator
from ingen.utils.run_configuration import RunConfiguration
from ingen.writer.writer import InterfaceWriter


class TestClass:
    pass


class TestRunConfiguration:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        config = {
            'formatter': 'CustomFormatter',
            'writer': 'CustomWriter',
            'generator': 'CustomGenerator'
        }
        self.config = RunConfiguration(config)

    def test_generator(self, monkeypatch):
        class GeneratorsStub:
            CustomGenerator = TestClass
        
        monkeypatch.setattr('ingen.utils.run_configuration.generators', GeneratorsStub())
        assert self.config.generator == TestClass

    def test_formatter(self, monkeypatch):
        class FormattersStub:
            CustomFormatter = TestClass
        
        monkeypatch.setattr('ingen.utils.run_configuration.formatters', FormattersStub())
        assert self.config.formatter == TestClass

    def test_writer(self, monkeypatch):
        class WritersStub:
            CustomWriter = TestClass
        
        monkeypatch.setattr('ingen.utils.run_configuration.writers', WritersStub())
        assert self.config.writer == TestClass

    def test_defaults(self):
        config = RunConfiguration({})
        assert config.generator == InterfaceGenerator
        assert config.writer == InterfaceWriter
        assert config.formatter == Formatter
