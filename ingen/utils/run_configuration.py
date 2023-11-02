#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import ingen.formatters as formatters
import ingen.generators as generators
import ingen.writer as writers


class RunConfiguration:
    def __init__(self, config):
        self._config = config

    @property
    def generator(self):
        generator_name = self.get_config_value('generator', 'InterfaceGenerator')
        return getattr(generators, generator_name)

    @property
    def writer(self):
        writer_name = self.get_config_value('writer', 'InterfaceWriter')
        return getattr(writers, writer_name)

    @property
    def formatter(self):
        formatter_name = self.get_config_value('formatter', 'Formatter')
        return getattr(formatters, formatter_name)

    def get_config_value(self, attr, default=None):
        return self._config.get(attr, default)

