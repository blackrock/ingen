#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import os

ENVIRONMENT_VAR_PATTERN = "$$"


class TestParseUtils:

    def test_var_starts_with_pattern_when_matches(self):
        assert '$$VAR'.startswith(ENVIRONMENT_VAR_PATTERN)

    def test_var_starts_with_pattern_when_does_not_matches(self):
        assert not 'VAR'.startswith(ENVIRONMENT_VAR_PATTERN)

    def test_get_environment_value_when_value_present(self, monkeypatch):
        monkeypatch.setenv('FILE_SOURCE', 'test/file/path/')
        assert os.getenv('FILE_SOURCE') == 'test/file/path/'

    def test_get_environment_value_when_value_not_present(self, monkeypatch):
        monkeypatch.delenv('FILE_SOURCE', raising=False)
        assert os.getenv('FILE_SOURCE') is None
