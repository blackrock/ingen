#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

import hvac
import hvac.exceptions

from ingen.utils.properties import properties


class AppSecrets:
    """
    Util class to get secrets stored in vault.
    """
    vault_client = None

    @classmethod
    def connect_client(cls):
        """Makes a new connection to Vault if not already connected"""
        url = properties.get_property("vault_url", "http://localhost:8200")
        if not cls.vault_client:
            cls.vault_client = hvac.Client(url=url)
            if not cls.vault_client.is_authenticated():
                raise Exception(f"Could not make connection to vault at {url}. Check authentication.")
            logging.info(f"Vault client connected: {cls.vault_client.is_authenticated()}")
        return cls.vault_client

    @classmethod
    def get_secret(cls, path, version=None):
        """
        Get secret value from vault secrets key-value store. If version is not provided latest version will
        be returned.
        """
        client = cls.connect_client()
        return client.secrets.kv.v2.read_secret_version(path, version)
