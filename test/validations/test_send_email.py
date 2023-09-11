#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from unittest.mock import patch, MagicMock

from ingen.utils.properties import properties
from ingen.validation import send_email


class TestScript(unittest.TestCase):

    def test_send_email(self):
        body = "test_body"
        subject = "test_subject"
        with patch('smtplib.SMTP', autospec=True) as mock_smtp:
            send_email.send_email('to_address', body, subject)
            instance = mock_smtp.return_value.__enter__.return_value
            self.assertEqual(instance.send_message.call_count, 1)

    def test_mail_server_other_host(self):
        with patch('sys.platform', MagicMock(return_value='linux')):
            fetched_value = send_email.determine_mailserver()
            expected_value = properties.get_property('mail.smtp.host')
            self.assertEqual(expected_value, fetched_value)


if __name__ == '__main__':
    unittest.main()
