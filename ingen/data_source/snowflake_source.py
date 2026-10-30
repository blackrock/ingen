#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

from ingen.data_source.source import DataSource
from ingen.reader.snowflake_reader import SnowflakeReader
from ingen.utils.properties import properties
from ingen.utils.sql_query_parser import SqlQueryParser
from ingen.utils.timer import log_time

log = logging.getLogger()

PROPERTY_PREFIX = 'datasource.snowflake.'

PASSWORD = 'snowflake'
KEY_PAIR = 'snowflake_jwt'
OAUTH = 'oauth'
EXTERNAL_BROWSER = 'externalbrowser'

# Credentials required by each authenticator, read from config.properties.
REQUIRED_CREDENTIALS = {
    PASSWORD: ['user', 'password'],
    KEY_PAIR: ['user', 'private_key_path'],
    OAUTH: ['token'],
    EXTERNAL_BROWSER: ['user'],
}

CREDENTIAL_KEYS = ['account', 'user', 'password', 'private_key_path', 'private_key_passphrase', 'token']
SESSION_KEYS = ['warehouse', 'database', 'schema', 'role']


class SnowflakeSource(DataSource):
    """
    This class represents snowflake database source.
    Connection details and credentials are read from config.properties (datasource.snowflake.*);
    session context (warehouse, database, schema, role) and the query are read from the source config.
    """

    def __init__(self, source, params_map=None):
        """
        Loads a SnowflakeSource
        :param source: Map which contains source data such as id, query, warehouse, database, etc.
        :param params_map: Map which contains runtime parameters such as query_params, run_date
        """
        super().__init__(source['id'])
        if source.get('temp_table_params'):
            # SqlQueryParser builds Sybase-style temp tables (#name, multiple statements), which Snowflake rejects.
            raise ValueError("temp_table_params is not supported for snowflake sources")
        self._src_data_checks = source.get('src_data_checks', [])
        self._query = SqlQueryParser().parse_query(source['query'], params_map)
        self._connection_params = self._build_connection_params(source)

    @staticmethod
    def _build_connection_params(source):
        credentials = {key: properties.get_property(PROPERTY_PREFIX + key) for key in CREDENTIAL_KEYS}
        if not credentials['account']:
            raise ValueError(f"Missing Snowflake property '{PROPERTY_PREFIX}account'")

        authenticator = SnowflakeSource._resolve_authenticator(source, credentials)
        missing = [PROPERTY_PREFIX + key for key in REQUIRED_CREDENTIALS[authenticator] if not credentials[key]]
        if missing:
            raise ValueError(f"Missing Snowflake properties for authenticator '{authenticator}': {', '.join(missing)}")

        params = {'account': credentials['account'], 'authenticator': authenticator}
        params.update({key: source[key] for key in SESSION_KEYS if source.get(key)})
        if credentials['user']:
            params['user'] = credentials['user']
        if authenticator == PASSWORD:
            params['password'] = credentials['password']
        elif authenticator == KEY_PAIR:
            params['private_key_file'] = credentials['private_key_path']
            if credentials['private_key_passphrase']:
                params['private_key_file_pwd'] = credentials['private_key_passphrase']
        elif authenticator == OAUTH:
            params['token'] = credentials['token']
        else:
            log.warning("Snowflake externalbrowser (SSO) authentication opens a browser window and is intended "
                        "for local use only. Use key pair, OAuth or password authentication for automated runs.")
        return params

    @staticmethod
    def _resolve_authenticator(source, credentials):
        """
        Uses the authenticator set in the source config, if any. Otherwise it is inferred from the configured
        credentials: private key > OAuth token > password. externalbrowser is never inferred, it must be explicit.
        """
        authenticator = source.get('authenticator')
        if authenticator:
            authenticator = str(authenticator).lower()
            if authenticator not in REQUIRED_CREDENTIALS:
                raise ValueError(f"Unsupported Snowflake authenticator '{authenticator}'. "
                                 f"Supported: {', '.join(REQUIRED_CREDENTIALS)}")
            return authenticator
        if credentials['private_key_path']:
            return KEY_PAIR
        if credentials['token']:
            return OAUTH
        if credentials['password']:
            return PASSWORD
        raise ValueError(f"No Snowflake credentials found. Set one of {PROPERTY_PREFIX}private_key_path, "
                         f"{PROPERTY_PREFIX}token or {PROPERTY_PREFIX}password in config.properties, "
                         f"or set 'authenticator: {EXTERNAL_BROWSER}' in the source for local SSO.")

    def fetch(self):
        """
        Executes the SQL query
        :return: A DataFrame created using the result of the query
        """
        # Imported lazily: the connector is slow to import and only needed when a snowflake source is used.
        import snowflake.connector
        reader = SnowflakeReader(snowflake.connector.connect(**self._connection_params))
        return self.fetch_data(reader)

    @log_time
    def fetch_data(self, reader):
        """
        returns a DataFrame of data fetched from SnowflakeSource.
        """
        return reader.execute(self._query)

    def fetch_validations(self):
        """
        Method to fetch validations from the source
        :return: list of dictionaries containing mentioned validations on all columns
        """
        return self._src_data_checks
