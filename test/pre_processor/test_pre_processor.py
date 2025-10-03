#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pytest
from unittest.mock import patch, Mock

import pandas as pd

from ingen.pre_processor.aggregator import Aggregator
from ingen.pre_processor.merger import Merger
from ingen.pre_processor.pre_processor import PreProcessor


class TestPreProcessor:

    @patch('ingen.pre_processor.pre_processor.PreProcessor.get_processor')
    def test_pre_process_calls_execute_when_preprocessing_present(self, pre_processor_mock):
        config = {'type': 'merge', 'source': ['source1'], 'key_column': 'id'}
        data = {'source1': pd.DataFrame()}
        processor_mock = Mock()

        pre_processor_mock.return_value = processor_mock

        obj = PreProcessor(config, data)
        obj.pre_process()
        processor_mock.execute.assert_called()

    @patch('ingen.pre_processor.pre_processor.PreProcessor.get_processor')
    def test_pre_process_doesnt_call_execute_when_no_preprocesing(self, pre_processor_mock):
        config = None
        source_data = {'source1': pd.DataFrame({'numbers': [1, 2, 3], 'colors': ['red', 'white', 'blue']})}
        processor_mock = Mock()

        pre_processor_mock.return_value = processor_mock

        obj = PreProcessor(config, source_data)
        result = obj.pre_process()
        pd.testing.assert_frame_equal(source_data['source1'], result)
        processor_mock.execute.assert_not_called()

    @patch('ingen.pre_processor.pre_processor.PreProcessor.get_processor')
    def test_pre_process_raise_exception_when_multiple_dataset_and_no_preprocessing(self, pre_processor_mock):
        config = None
        data = {'source1': pd.DataFrame(), 'source2': pd.DataFrame()}
        processor_mock = Mock()
        pre_processor_mock.return_value = processor_mock
        obj = PreProcessor(config, data)
        data_actual = obj.pre_process()
        processor_mock.execute.assert_not_called()

    def test_get_processor_returns_proper_processor(self):
        config = {'type': 'merge', 'source': ['source1'], 'key_column': 'id'}
        config2 = {'type': 'aggregate', 'source': ['source1'], 'key_column': 'id'}
        data = {'source1': pd.DataFrame(), 'source2': pd.DataFrame()}
        obj = PreProcessor(config, data)
        obj2 = PreProcessor(config2, data)

        processor = obj.get_processor(config)
        processor2 = obj2.get_processor(config2)

        assert isinstance(processor, Merger)
        assert isinstance(processor2, Aggregator)

    def test_get_processor_raises_exception_when_type_not_known(self):
        config = {'type': 'abcd', 'source': ['source1'], 'key_column': 'id'}
        data = {'source1': pd.DataFrame(), 'source2': pd.DataFrame()}
        obj = PreProcessor(config, data)
        message = "pre-processing abcd is not recognized"
        with pytest.raises(NameError, match=message):
            obj.get_processor(config)

    def test_empty_source_data(self):
        config = {'type': 'any_pre_processor_type'}
        data = []
        error_message = 'Source data cannot be empty'
        with pytest.raises(ValueError, match=error_message):
            PreProcessor(config, data)
