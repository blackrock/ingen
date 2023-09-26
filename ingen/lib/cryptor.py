#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import base64
import hashlib
import hmac
import json
import subprocess
from functools import lru_cache

from Crypto.Cipher import AES

from ingen.utils.app_secrets import AppSecrets
from ingen.utils.properties import properties

"""
Encryption methods using the AES/CTR/NoPadding algorithm using the 256bit AES Key.

"""


class Cryptor:
    def __init__(self):
        self.config = {'vault_path': properties.get_property('cryptor.vault_path'),
                       'hmac_key_name': properties.get_property('cryptor.hmac_key_name'),
                       'aes_key_name': properties.get_property('cryptor.aes_key_name')}

    @lru_cache(maxsize=2)
    def __decrypt_gpg_kek(self, encoded_kek):
        decoded_result = base64.b64decode(encoded_kek.encode('utf-8')).decode('utf-8')
        query = f"echo '{decoded_result}' | gpg -d --no-tty"
        orig = subprocess.check_output(query, shell=True).decode('utf-8').strip()
        return orig

    @lru_cache(maxsize=10)
    def __fetch_key(self, key_name, key_version=None):
        """
        Method to fetch Keys from the sybase db using the DSREAD access.
        :param key_name: Name of the key at this path
        :param key_version: key version, if not provided latest version will be returned
        :return: String kev value.
        """
        response = AppSecrets.get_secret(path=self.config['vault_path'], version=key_version)
        return response["data"]["data"][key_name], key_version

    @lru_cache(maxsize=1)
    def __get_hmac_key(self, key_version=None):
        """
        Placeholder method to get the HMAC key from the KMS.
        :return: Key Bytes
        """
        encoded_key, db_key_version = self.__fetch_key(self.config['hmac_key_name'], key_version)
        hmac_key = self.__decrypt_gpg_kek(encoded_key)

        return bytes(hmac_key, 'utf-8'), db_key_version

    @lru_cache(maxsize=1)
    def __get_key(self, key_version=None):
        """
        Placeholder method to get the AES key from the KMS.
        :return: Key Bytes
        """
        encoded_key, db_key_version = self.__fetch_key(self.config['aes_key_name'], key_version)
        aes = self.__decrypt_gpg_kek(encoded_key)

        return bytes(aes, 'utf-8'), db_key_version

    def encrypt(self, plaintext):
        """
        Encryption method using the AES/CTR/NoPadding.
        While encrypting we always want to use the latest key
        hence we pass the key_version as none.
        :param plaintext: The message to be encrypted.
        :return: JSON of format cipher and nonce.
        """
        aes_key, db_key_version = self.__get_key()
        hmac_key, db_hmac_version = self.__get_hmac_key()
        plaintext = str(plaintext)
        data_bytes = bytes(plaintext, 'utf-8')
        aes_obj = AES.new(aes_key, AES.MODE_CTR)
        cipher_text = aes_obj.encrypt(data_bytes)
        encode_cipher = base64.b64encode(cipher_text).decode('utf-8')
        encode_nonce = base64.b64encode(aes_obj.nonce).decode('utf-8')
        hmac_encode = hmac.new(hmac_key, msg=bytes(encode_cipher, 'utf-8'),
                               digestmod=hashlib.sha256).hexdigest()
        json_result = json.dumps(
            {'cipher': encode_cipher, 'nonce': encode_nonce, 'mac': hmac_encode, 'key_version': db_key_version,
             'hmac_version': db_hmac_version})
        return base64.b64encode(bytes(json_result, 'utf-8')).decode('utf-8')

    def decrypt(self, message):
        """
        The Decryption method to take the JSON object of type Ciper and Nonce.
        :param message: JSON Object.
        :return: String message.
        """
        decoded_message = base64.b64decode(message.encode('utf-8')).decode('utf-8')
        cipher_dict = json.loads(decoded_message)
        key_version = cipher_dict['key_version']
        hmac_version = cipher_dict['hmac_version']
        aes_key, db_key_version = self.__get_key(key_version)
        hmac_key, db_hmac_version = self.__get_hmac_key(hmac_version)
        hmac_encode = hmac.new(hmac_key, msg=bytes(cipher_dict['cipher'], 'utf-8'),
                               digestmod=hashlib.sha256).hexdigest()
        if not hmac_encode == cipher_dict['mac']:
            raise Exception("Hmac Validation Failed, the cipher seems to be tampered.")
        aes_obj = AES.new(aes_key, AES.MODE_CTR, nonce=base64.b64decode(cipher_dict['nonce'].encode('utf-8')))
        raw_bytes = aes_obj.decrypt(base64.b64decode(cipher_dict['cipher'].encode('utf-8')))

        return raw_bytes.decode('utf-8')
