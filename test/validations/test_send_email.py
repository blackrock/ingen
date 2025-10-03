#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from ingen.utils.properties import properties
from ingen.validation import send_email


class TestScript:

    def test_send_email(self, monkeypatch):
        body = "test_body"
        subject = "test_subject"
        
        class MockSMTP:
            def __init__(self, *args, **kwargs):
                self.send_message_calls = 0
            
            def __enter__(self):
                return self
            
            def __exit__(self, *args):
                pass
            
            def send_message(self, *args, **kwargs):
                self.send_message_calls += 1
        
        mock_smtp_instance = MockSMTP()
        
        def mock_smtp_constructor(*args, **kwargs):
            return mock_smtp_instance
        
        monkeypatch.setattr("smtplib.SMTP", mock_smtp_constructor)
        
        send_email.send_email('to_address', body, subject)
        assert mock_smtp_instance.send_message_calls == 1

    def test_mail_server_other_host(self, monkeypatch):
        monkeypatch.setattr("sys.platform", "linux")
        
        fetched_value = send_email.determine_mailserver()
        expected_value = properties.get_property('mail.smtp.host')
        assert expected_value == fetched_value