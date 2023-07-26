import base64
import subprocess
import unittest
from unittest.mock import patch

from ingen.lib.cryptor import Cryptor

"""
Unit tests for the cryptor methods.
"""


@patch('ingen.lib.cryptor.get_property', side_effect=[
    "misdb",
    "mock_keys",
    "POC_HMAC_DEV_KEK_TESTING",
    "POC_AES_DEV_KEK_TESTING"
])
class CryptorTest(unittest.TestCase):

    @patch.object(Cryptor, '_Cryptor__fetch_key', return_value=('boom', 1))
    @patch.object(Cryptor, "_Cryptor__decrypt_gpg_kek", return_value='boom')
    def testGetKeyUseGPG(self, gpg_decrypt, fetch_key, blkconfig):
        cryptor = Cryptor()
        self.assertEqual((bytes('boom', 'utf-8'), 1), cryptor._Cryptor__get_key())

    @patch.object(Cryptor, '_Cryptor__fetch_key', return_value=('boom', 1))
    @patch.object(Cryptor, "_Cryptor__decrypt_gpg_kek", return_value='boom')
    def testGetHmacKeyUseGPG(self, gpg_decrypt, fetch_key, blkconfig):
        cryptor = Cryptor()
        self.assertEqual((bytes('boom', 'utf-8'), 1), cryptor._Cryptor__get_hmac_key())

    @patch.object(subprocess, "check_output", return_value=b"called_sub_process")
    def testDecryptGpgKek(self, mock_subprocess, blkutils):
        cryptor = Cryptor()
        encoded = base64.b64encode(b"encoded_string").decode('utf-8')
        self.assertEqual("called_sub_process", cryptor._Cryptor__decrypt_gpg_kek(encoded))

    @patch.object(Cryptor, "_Cryptor__fetch_key", return_value=("34DDA783B8C979C881E0EB3C8185825B", 3))
    @patch.object(Cryptor, "_Cryptor__decrypt_gpg_kek", return_value="34DDA783B8C979C881E0EB3C8185825B")
    def testGetKeyGpg(self, mock_fetch_key, mock_decrypt_gpg_key, blkutils):
        cryptor = Cryptor()
        self.assertEqual(cryptor._Cryptor__get_key(), (bytes("34DDA783B8C979C881E0EB3C8185825B", "utf-8"), 3))

    @patch.object(Cryptor, "_Cryptor__fetch_key", return_value=("e4ee804adfbc82376daba92960449d", 3))
    @patch.object(Cryptor, "_Cryptor__decrypt_gpg_kek", return_value="e4ee804adfbc82376daba92960449d")
    def testGetHmacKeyGpg(self, mock_fetch_key, mock_decrypt_gpg_key, blkutils):
        cryptor = Cryptor()
        self.assertEqual(cryptor._Cryptor__get_hmac_key(), (bytes("e4ee804adfbc82376daba92960449d", "utf-8"), 3))

    @patch.object(Cryptor, "_Cryptor__get_key", return_value=(bytes('34DDA783B8C979C881E0EB3C8185825B', 'utf-8'), 3))
    @patch.object(Cryptor, "_Cryptor__get_hmac_key",
                  return_value=(bytes('e4ee804adfbc82376daba92960449d', 'utf-8'), 3))
    def testEncrypt(self, mock_get_key, mock_hmac_key, blkutils):
        """
        Its practically impossible to test the encrypt function as there is a random
        nonce that is generated and the ciphertext is always going to be different,
        so we encrypt the string and decrypt the cipher to check if the string is intact.

        """
        message_int = 123456
        message_str = "hello"
        cryptor = Cryptor()
        self.assertEqual(cryptor.decrypt(cryptor.encrypt(message_int)), str(message_int))
        self.assertEqual(cryptor.decrypt(cryptor.encrypt(message_str)), message_str)

    @patch.object(Cryptor, "_Cryptor__get_key", return_value=(bytes('34DDA783B8C979C881E0EB3C8185825B', 'utf-8'), 3))
    @patch.object(Cryptor, "_Cryptor__get_hmac_key",
                  return_value=(bytes('e4ee804adfbc82376daba92960449d', 'utf-8'), 3))
    def testDecrypt(self, mock_get_key, mock_hmac_key, blkutils):
        """
        Unit test the decryptor method.
        :return: None
        """
        cryptor = Cryptor()
        encrypted = 'eyJjaXBoZXIiOiAibDhhQ3lmQTQiLCAibm9uY2UiOiAiK3UwY2dvSXdSbWc9Iiw' \
                    'gIm1hYyI6ICI2MjY0NjQ3MmNiNjhlZTQ2YzVkOWViOWIyMmU3ZTlkYmU0MTkyOTN' \
                    'lNjNlNTI3Yzk4NTEwNDFiMTY1OTAxYzE1IiwgImtleV92ZXJzaW9uIjogMywgImh' \
                    'tYWNfdmVyc2lvbiI6IDN9 '
        self.assertEqual(cryptor.decrypt(encrypted), "123456")

    @patch.object(Cryptor, "_Cryptor__get_key", return_value=(bytes('34DDA783B8C979C881E0EB3C8185825B', 'utf-8'), 3))
    @patch.object(Cryptor, "_Cryptor__get_hmac_key",
                  return_value=(bytes('e4ee804adfbc82376daba92960449d', 'utf-8'), 3))
    def testHmacTampering(self, mock_get_key, mock_hmac_key, blkutils):
        """
        Unit test the decryptor method with the Hmac value changed, which will result in the code breaking
        as the calculated Hmac will vary from the mac provided in the input JSON.
        :return: None
        """
        cryptor = Cryptor()
        encrypted = 'eyJjaXBoZXIiOiAicE5kbVg3Zz0iLCAibm9uY2UiOiAiQnZSb1pmSjZsc' \
                    'zA9IiwgIm1hYyI6ICIwMWVjOWYzZDM4MmVhMTI4OTU3MzcxZTJiYWE5Zj' \
                    'IyYTYxNTBmNGNiZWU2YTJmMTJhMzU1YmYxMDNlNGU0YmRkIiwia2V5X3Z' \
                    'lcnNpb24iOiAzLCAiaG1hY192ZXJzaW9uIjogM30g'
        with self.assertRaises(Exception):
            cryptor.decrypt(encrypted)


if __name__ == '__main__':
    unittest.main()
