#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from unittest.mock import patch

from ingen.validation.notification import get_attributes, email_attributes


class MyTestCase(unittest.TestCase):
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
        self.assertEqual(expected_output, actual_output)

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
        self.assertEqual(expected_output, actual_output)

    @patch('ingen.validation.notification.send_email')
    def test_email_attributes(self, mock_send_email):
        params = {'run_date': 20220708}
        validation_action = {
            'send_email': ['abc.abc@abc.com']
        }
        validation_summary = {
            'name_1': [{'evaluated_expectations': 12, 'successful_expectations': 9, 'unsuccessful_expectations': 3,
                        'success_percent': 75.0}, 'severity : warning']
        }
        email_attributes(params, validation_action, validation_summary)
        mock_send_email.assert_called_with(validation_action['send_email'],
                                           '\nValidation Status for source: name_1\nFile Name: None\n\nseverity : warning\n',
                                           f'Data Validation Failure ({params["run_date"]})')

    @patch('ingen.validation.notification.send_email')
    def test_email_attributesif_outputfile_is_none(self, mock_send_email):
        params = {'run_date': 20220708}
        validation_action = {
            'send_email': ['abc.abc@abc.com']
        }
        validation_summary = {
            'name_1': [{'evaluated_expectations': 12, 'successful_expectations': 9, 'unsuccessful_expectations': 3,
                        'success_percent': 75.0}, 'severity : warning']
        }
        email_attributes(params, validation_action, validation_summary)
        mock_send_email.assert_called_with(validation_action['send_email'],
                                           '\nValidation Status for source: name_1\nFile Name: None\n\nseverity : warning\n',
                                           f'Data Validation Failure ({params["run_date"]})')

    @patch('ingen.validation.notification.send_email')
    def test_email_attributes_when_severity_blocker(self, mock_send_email):
        params = {'run_date': 20220708}
        validation_action = {
            'send_email': ['abc.abc@abc.com']
        }
        validation_summary = {
            'name_1': [{'evaluated_expectations': 12, 'successful_expectations': 9, 'unsuccessful_expectations': 3,
                        'success_percent': 75.0}, 'severity : blocker']
        }
        self.assertRaises(ValueError, email_attributes, params, validation_action, validation_summary)


if __name__ == '__main__':
    unittest.main()
