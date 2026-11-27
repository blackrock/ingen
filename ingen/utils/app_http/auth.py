#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import asyncio
import base64
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from aiohttp import BasicAuth

from ingen.utils.properties import properties

log = logging.getLogger()


class OAuth2Token:
    """Wraps an OAuth 2.0 token response with expiry tracking.

    A typical token response contains:
        access_token (str): The token to use in API calls
        token_type (str): Usually "Bearer"
        expires_in (int): Token lifetime in seconds
        refresh_token (str, optional): Token to obtain a new access_token
    """

    def __init__(self, token_data):
        self._data = token_data
        if token_data.get('expires_in') is not None:
            self._data['expires_at'] = int(time.time()) + int(token_data['expires_in'])

    @property
    def access_token(self):
        return self._data.get('access_token')

    @property
    def refresh_token(self):
        return self._data.get('refresh_token')

    def is_expired(self, leeway=60):
        """Check if the token is expired (or will expire within leeway seconds).

        :param leeway: Seconds before actual expiry to consider the token expired.
        :return: True if expired, False if valid, None if no expiry info.
        """
        expires_at = self._data.get('expires_at')
        if expires_at is None:
            return None
        return (expires_at - leeway) < time.time()


class OAuth2Client:
    """Manages the OAuth 2.0 token lifecycle for a single auth configuration.

    Handles token fetching, caching, and refresh for client_credentials
    and password grant types.
    """

    def __init__(self, auth_config):
        self._grant_type = auth_config.get('grant_type')
        self._token_url = auth_config.get('token_url')
        scope = auth_config.get('scope')
        self._scope = ' '.join(scope) if isinstance(scope, list) else scope
        self._auth_method = auth_config.get('method', 'client_secret_basic')

        self._validate_config(auth_config)

        self._client_id = properties.get_property('api_auth.client_id')
        self._client_secret = properties.get_property('api_auth.client_secret')

        self._username = None
        self._password = None
        if self._grant_type == 'password':
            self._username = properties.get_property('api_auth.username')
            self._password = properties.get_property('api_auth.password')

        self._token = None
        self._lock = asyncio.Lock()

    @staticmethod
    def _validate_config(auth_config):
        """Validate that all required fields are present in the auth config."""
        required = ['token_url']
        missing = [f for f in required if not auth_config.get(f)]
        if missing:
            raise ValueError(f"OAuth2 auth config missing required fields: {missing}")

    async def ensure_active_token(self, session):
        """Return a valid token, fetching or refreshing as needed.

        Uses asyncio.Lock to prevent concurrent token refresh from multiple consumer tasks.

        :param session: aiohttp.ClientSession
        :return: OAuth2Token
        """
        async with self._lock:
            if self._token and not self._token.is_expired():
                return self._token

            if self._token and self._token.refresh_token:
                return await self._refresh_token(session)

            return await self._fetch_token(session)

    def _attach_client_credentials(self, headers, body):
        """Attach client credentials to the request per auth method.

        :param headers: dict of HTTP headers (mutated in place)
        :param body: dict of POST body params (mutated in place)
        """
        if self._auth_method == 'client_secret_basic':
            credentials = f"{self._client_id}:{self._client_secret}"
            encoded = base64.b64encode(credentials.encode('latin1')).decode('latin1')
            headers['Authorization'] = f"Basic {encoded}"
        elif self._auth_method == 'client_secret_post':
            body['client_id'] = self._client_id
            body['client_secret'] = self._client_secret

    async def _fetch_token(self, session):
        """Fetch a new access token from the token endpoint.

        :param session: aiohttp.ClientSession
        :return: OAuth2Token
        """
        body = {'grant_type': self._grant_type}
        if self._scope:
            body['scope'] = self._scope
        if self._grant_type == 'password':
            body['username'] = self._username
            body['password'] = self._password

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self._attach_client_credentials(headers, body)

        log.info(f"Fetching OAuth2 token from {self._token_url} (grant_type={self._grant_type})")
        async with session.post(self._token_url, data=body, headers=headers) as response:
            if response.status != 200:
                text = await response.text()
                raise ConnectionError(
                    f"OAuth2 token request failed with status {response.status}: {text}"
                )
            token_data = await response.json()

        self._token = OAuth2Token(token_data)
        log.info("OAuth2 token acquired successfully")
        return self._token

    async def _refresh_token(self, session):
        """Refresh the access token using the refresh_token grant.

        :param session: aiohttp.ClientSession
        :return: OAuth2Token
        """
        body = {
            'grant_type': 'refresh_token',
            'refresh_token': self._token.refresh_token,
        }
        if self._scope:
            body['scope'] = self._scope

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self._attach_client_credentials(headers, body)

        log.info(f"Refreshing OAuth2 token from {self._token_url}")
        async with session.post(self._token_url, data=body, headers=headers) as response:
            if response.status != 200:
                text = await response.text()
                log.warning(f"OAuth2 token refresh failed ({response.status}), re-authenticating")
                return await self._fetch_token(session)
            token_data = await response.json()

        if 'refresh_token' not in token_data and self._token.refresh_token:
            token_data['refresh_token'] = self._token.refresh_token

        self._token = OAuth2Token(token_data)
        log.info("OAuth2 token refreshed successfully")
        return self._token


# Module-level cache of OAuth2Client instances, keyed by (token_url, scope, method)
_oauth2_clients = {}


@dataclass
class AuthResult:
    """Result of auth resolution. Carries either BasicAuth or Bearer token headers."""
    auth: Optional[BasicAuth] = None
    headers: Optional[dict] = field(default_factory=dict)


def basic_auth_handler(auth_config):
    """Handle BasicAuth authentication.

    :param auth_config: dict with auth configuration from YAML
    :return: AuthResult with aiohttp.BasicAuth
    """
    try:
        user = properties.get_property('api_auth.username')
        password = properties.get_property('api_auth.password')
        return AuthResult(auth=BasicAuth(user, password))
    except Exception as e:
        log.exception(f"Error while getting the property username/pwd for api call: {e}")
        return AuthResult()


async def oauth2_auth_handler(session, auth_config):
    """Handle OAuth2 authentication (client_credentials and password grants).

    :param session: aiohttp.ClientSession
    :param auth_config: dict with auth configuration from YAML
    :return: AuthResult with Bearer token header
    """
    scope = auth_config.get('scope', '')
    if isinstance(scope, list):
        scope = ' '.join(scope)
    cache_key = (auth_config.get('token_url'), scope, auth_config.get('method', 'client_secret_basic'))
    if cache_key not in _oauth2_clients:
        _oauth2_clients[cache_key] = OAuth2Client(auth_config)

    client = _oauth2_clients[cache_key]
    token = await client.ensure_active_token(session)
    return AuthResult(headers={'Authorization': f"Bearer {token.access_token}"})


def pre_obtained_token_handler(auth_config):
    """Handle pre-obtained token authentication.

    :param auth_config: dict with auth configuration from YAML
    :return: AuthResult with Bearer token header
    """
    access_token = properties.get_property('api_auth.access_token')
    if not access_token:
        raise ValueError("Could not read access token from properties. "
                         "Check property key: api_auth.access_token")
    return AuthResult(headers={'Authorization': f"Bearer {access_token}"})


async def get_auth(session, auth_config):
    """Top-level auth dispatcher. Resolves auth config to an AuthResult.

    :param session: aiohttp.ClientSession
    :param auth_config: dict with 'type' key, or None for no auth
    :return: AuthResult
    """
    if not auth_config:
        return AuthResult()

    auth_type = auth_config.get('type')

    if auth_type == 'BasicAuth':
        return basic_auth_handler(auth_config)
    elif auth_type == 'OAuth2':
        grant_type = auth_config.get('grant_type')
        if grant_type == 'token':
            return pre_obtained_token_handler(auth_config)
        elif grant_type in ('client_credentials', 'password'):
            return await oauth2_auth_handler(session, auth_config)
        else:
            raise ValueError(f"Unsupported OAuth2 grant_type: {grant_type}")
    else:
        raise ValueError(f"Unsupported auth type: {auth_type}")
