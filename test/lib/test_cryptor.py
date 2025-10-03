#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import base64
import subprocess
import pytest

from ingen.lib.cryptor import Cryptor

"""
Unit tests for the cryptor methods.
"""


@pytest.fixture(autouse=True)
def _stub_properties(monkeypatch):
    config = {
        'cryptor.vault_path': 'misdb',
        'cryptor.hmac_key_name': 'POC_HMAC_DEV_KEK_TESTING',
        'cryptor.aes_key_name': 'POC_AES_DEV_KEK_TESTING',
    }

    def fake_get_property(key):
        return config[key]

    monkeypatch.setattr('ingen.lib.cryptor.properties.get_property', fake_get_property)


def test_get_key_use_gpg(monkeypatch):
    monkeypatch.setattr(Cryptor, '_Cryptor__fetch_key',
                        lambda self, key_name, key_version=None: ('boom', 1))
    monkeypatch.setattr(Cryptor, '_Cryptor__decrypt_gpg_kek',
                        lambda self, encoded_kek: 'boom')

    cryptor = Cryptor()
    assert (bytes('boom', 'utf-8'), 1) == cryptor._Cryptor__get_key()


def test_get_hmac_key_use_gpg(monkeypatch):
    monkeypatch.setattr(Cryptor, '_Cryptor__fetch_key',
                        lambda self, key_name, key_version=None: ('boom', 1))
    monkeypatch.setattr(Cryptor, '_Cryptor__decrypt_gpg_kek',
                        lambda self, encoded_kek: 'boom')

    cryptor = Cryptor()
    assert (bytes('boom', 'utf-8'), 1) == cryptor._Cryptor__get_hmac_key()


def test_decrypt_gpg_kek(monkeypatch):
    monkeypatch.setattr(subprocess, 'check_output',
                        lambda query, shell=True: b"called_sub_process")
    cryptor = Cryptor()
    encoded = base64.b64encode(b"encoded_string").decode('utf-8')
    assert "called_sub_process" == cryptor._Cryptor__decrypt_gpg_kek(encoded)


def test_get_key_gpg(monkeypatch):
    monkeypatch.setattr(Cryptor, '_Cryptor__fetch_key',
                        lambda self, key_name, key_version=None: ("34DDA783B8C979C881E0EB3C8185825B", 3))
    monkeypatch.setattr(Cryptor, '_Cryptor__decrypt_gpg_kek',
                        lambda self, encoded_kek: "34DDA783B8C979C881E0EB3C8185825B")
    cryptor = Cryptor()
    assert cryptor._Cryptor__get_key() == (bytes("34DDA783B8C979C881E0EB3C8185825B", "utf-8"), 3)


def test_get_hmac_key_gpg(monkeypatch):
    monkeypatch.setattr(Cryptor, '_Cryptor__fetch_key',
                        lambda self, key_name, key_version=None: ("e4ee804adfbc82376daba92960449d", 3))
    monkeypatch.setattr(Cryptor, '_Cryptor__decrypt_gpg_kek',
                        lambda self, encoded_kek: "e4ee804adfbc82376daba92960449d")
    cryptor = Cryptor()
    assert cryptor._Cryptor__get_hmac_key() == (bytes("e4ee804adfbc82376daba92960449d", "utf-8"), 3)


def test_encrypt(monkeypatch):
    monkeypatch.setattr(Cryptor, "_Cryptor__get_key",
                        lambda self, key_version=None: (bytes('34DDA783B8C979C881E0EB3C8185825B', 'utf-8'), 3))
    monkeypatch.setattr(Cryptor, "_Cryptor__get_hmac_key",
                        lambda self, key_version=None: (bytes('e4ee804adfbc82376daba92960449d', 'utf-8'), 3))

    message_int = 123456
    message_str = "hello"
    cryptor = Cryptor()
    assert cryptor.decrypt(cryptor.encrypt(message_int)) == str(message_int)
    assert cryptor.decrypt(cryptor.encrypt(message_str)) == message_str


def test_decrypt(monkeypatch):
    monkeypatch.setattr(Cryptor, "_Cryptor__get_key",
                        lambda self, key_version=None: (bytes('34DDA783B8C979C881E0EB3C8185825B', 'utf-8'), 3))
    monkeypatch.setattr(Cryptor, "_Cryptor__get_hmac_key",
                        lambda self, key_version=None: (bytes('e4ee804adfbc82376daba92960449d', 'utf-8'), 3))

    cryptor = Cryptor()
    encrypted = 'eyJjaXBoZXIiOiAibDhhQ3lmQTQiLCAibm9uY2UiOiAiK3UwY2dvSXdSbWc9Iiw' \
                'gIm1hYyI6ICI2MjY0NjQ3MmNiNjhlZTQ2YzVkOWViOWIyMmU3ZTlkYmU0MTkyOTN' \
                'lNjNlNTI3Yzk4NTEwNDFiMTY1OTAxYzE1IiwgImtleV92ZXJzaW9uIjogMywgImh' \
                'tYWNfdmVyc2lvbiI6IDN9 '
    assert cryptor.decrypt(encrypted) == "123456"


def test_hmac_tampering(monkeypatch):
    monkeypatch.setattr(Cryptor, "_Cryptor__get_key",
                        lambda self, key_version=None: (bytes('34DDA783B8C979C881E0EB3C8185825B', 'utf-8'), 3))
    monkeypatch.setattr(Cryptor, "_Cryptor__get_hmac_key",
                        lambda self, key_version=None: (bytes('e4ee804adfbc82376daba92960449d', 'utf-8'), 3))

    cryptor = Cryptor()
    encrypted = 'eyJjaXBoZXIiOiAicE5kbVg3Zz0iLCAibm9uY2UiOiAiQnZSb1pmSjZsc' \
                'zA9IiwgIm1hYyI6ICIwMWVjOWYzZDM4MmVhMTI4OTU3MzcxZTJiYWE5Zj' \
                'IyYTYxNTBmNGNiZWU2YTJmMTJhMzU1YmYxMDNlNGU0YmRkIiwia2V5X3Z' \
                'lcnNpb24iOiAzLCAiaG1hY192ZXJzaW9uIjogM30g'
    with pytest.raises(Exception):
        cryptor.decrypt(encrypted)
