#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pytest

from ingen.validation.notification import get_attributes, email_attributes


class TestNotification:
    def test_get_attributes(self):
        params = {'run_date': 20220708, 'infile': 'test/file.xlsx'}
        validation_action = {
            'send_email': ['abc.abc@abc.com']
        }
        expected_output = {
            'run_date': 20220708,
            'validate_action_to_adr': ['abc.abc@abc.com'],
            'file_name': 'file.xlsx'
        }
        actual_output = get_attributes(params, validation_action)
        assert expected_output == actual_output

    def test_get_attributes_if_outputfile_is_none(self):
        params = {'run_date': 20220708, 'infile': 'test/file.xlsx'}
        validation_action = {
            'send_email': ['abc.abc@abc.com']
        }
        expected_output = {
            'run_date': 20220708,
            'validate_action_to_adr': ['abc.abc@abc.com'],
            'file_name': 'file.xlsx'
        }
        actual_output = get_attributes(params, validation_action)
        assert expected_output == actual_output

    def test_email_attributes(self, monkeypatch):
        params = {'run_date': 20220708}
        validation_action = {
            'send_email': ['abc.abc@abc.com']
        }
        validation_summary = {
            'name_1': [{'evaluated_expectations': 12, 'successful_expectations': 9, 'unsuccessful_expectations': 3,
                        'success_percent': 75.0}, 'severity : warning']
        }
        
        class MockSendEmail:
            def __init__(self):
                self.calls = []
            
            def __call__(self, to_addresses, body, subject):
                self.calls.append((to_addresses, body, subject))
        
        mock_send_email = MockSendEmail()
        monkeypatch.setattr("ingen.validation.notification.send_email", mock_send_email)
        
        email_attributes(params, validation_action, validation_summary)
        
        expected_call = (
            validation_action['send_email'],
            '\nValidation Status for source: name_1\nFile Name: None\n\nseverity : warning\n',
            f'Data Validation Failure ({params["run_date"]})'
        )
        assert mock_send_email.calls[0] == expected_call

    def test_email_attributes_if_outputfile_is_none(self, monkeypatch):
        params = {'run_date': 20220708}
        validation_action = {
            'send_email': ['abc.abc@abc.com']
        }
        validation_summary = {
            'name_1': [{'evaluated_expectations': 12, 'successful_expectations': 9, 'unsuccessful_expectations': 3,
                        'success_percent': 75.0}, 'severity : warning']
        }
        
        class MockSendEmail:
            def __init__(self):
                self.calls = []
            
            def __call__(self, to_addresses, body, subject):
                self.calls.append((to_addresses, body, subject))
        
        mock_send_email = MockSendEmail()
        monkeypatch.setattr("ingen.validation.notification.send_email", mock_send_email)
        
        email_attributes(params, validation_action, validation_summary)
        
        expected_call = (
            validation_action['send_email'],
            '\nValidation Status for source: name_1\nFile Name: None\n\nseverity : warning\n',
            f'Data Validation Failure ({params["run_date"]})'
        )
        assert mock_send_email.calls[0] == expected_call

    def test_email_attributes_when_severity_blocker(self, monkeypatch):
        params = {'run_date': 20220708}
        validation_action = {
            'send_email': ['abc.abc@abc.com']
        }
        validation_summary = {
            'name_1': [{'evaluated_expectations': 12, 'successful_expectations': 9, 'unsuccessful_expectations': 3,
                        'success_percent': 75.0}, 'severity : blocker']
        }
        
        # Mock send_email to avoid actual email sending
        class MockSendEmail:
            def __call__(self, *args, **kwargs):
                pass
        
        mock_send_email = MockSendEmail()
        monkeypatch.setattr("ingen.validation.notification.send_email", mock_send_email)
        
        with pytest.raises(ValueError):
            email_attributes(params, validation_action, validation_summary)