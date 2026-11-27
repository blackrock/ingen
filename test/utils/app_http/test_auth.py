#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import asyncio
import base64
import unittest
from unittest.mock import patch, AsyncMock, MagicMock

from aiohttp import BasicAuth

from ingen.utils.app_http.auth import (
    OAuth2Token,
    OAuth2Client,
    AuthResult,
    basic_auth_handler,
    oauth2_auth_handler,
    pre_obtained_token_handler,
    get_auth,
    _oauth2_clients,
)


class TestOAuth2Token(unittest.TestCase):

    def test_token_not_expired(self):
        token = OAuth2Token({'access_token': 'abc', 'expires_in': 3600})
        self.assertFalse(token.is_expired())

    def test_token_expired(self):
        token = OAuth2Token({'access_token': 'abc', 'expires_in': 0})
        self.assertTrue(token.is_expired())

    def test_token_expired_within_leeway(self):
        token = OAuth2Token({'access_token': 'abc', 'expires_in': 30})
        self.assertTrue(token.is_expired(leeway=60))

    def test_token_without_expires_in(self):
        token = OAuth2Token({'access_token': 'abc'})
        self.assertIsNone(token.is_expired())

    def test_access_token_property(self):
        token = OAuth2Token({'access_token': 'my_token', 'expires_in': 3600})
        self.assertEqual('my_token', token.access_token)

    def test_refresh_token_present(self):
        token = OAuth2Token({
            'access_token': 'abc',
            'refresh_token': 'refresh_123',
            'expires_in': 3600
        })
        self.assertEqual('refresh_123', token.refresh_token)

    def test_refresh_token_absent(self):
        token = OAuth2Token({'access_token': 'abc', 'expires_in': 3600})
        self.assertIsNone(token.refresh_token)


class TestBasicAuthHandler(unittest.TestCase):

    @patch('ingen.utils.app_http.auth.properties')
    def test_basic_auth_returns_basic_auth(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.username': 'user',
            'api_auth.password': 'pass'
        }.get(key)
        auth_config = {'type': 'BasicAuth'}
        result = basic_auth_handler(auth_config)
        self.assertIsInstance(result, AuthResult)
        self.assertIsInstance(result.auth, BasicAuth)

    @patch('ingen.utils.app_http.auth.properties')
    def test_basic_auth_returns_empty_on_error(self, mock_properties):
        mock_properties.get_property.side_effect = Exception("property not found")
        auth_config = {'type': 'BasicAuth'}
        result = basic_auth_handler(auth_config)
        self.assertIsNone(result.auth)


class TestPreObtainedTokenHandler(unittest.TestCase):

    @patch('ingen.utils.app_http.auth.properties')
    def test_pre_obtained_token(self, mock_properties):
        mock_properties.get_property.return_value = 'my_static_token'
        auth_config = {
            'type': 'OAuth2',
            'grant_type': 'token',
        }
        result = pre_obtained_token_handler(auth_config)
        self.assertEqual({'Authorization': 'Bearer my_static_token'}, result.headers)
        self.assertIsNone(result.auth)

    @patch('ingen.utils.app_http.auth.properties')
    def test_pre_obtained_token_missing(self, mock_properties):
        mock_properties.get_property.return_value = None
        auth_config = {
            'type': 'OAuth2',
            'grant_type': 'token',
        }
        with self.assertRaises(ValueError):
            pre_obtained_token_handler(auth_config)


class TestOAuth2Client(unittest.TestCase):

    def setUp(self):
        # Clear the module-level cache before each test
        _oauth2_clients.clear()
        self.auth_config = {
            'type': 'OAuth2',
            'grant_type': 'client_credentials',
            'token_url': 'https://auth.example.com/token',
            'scope': 'read',
            'method': 'client_secret_basic',
        }
        self.token_response = {
            'access_token': 'test_access_token',
            'token_type': 'Bearer',
            'expires_in': 3600,
        }

    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def _make_mock_session(self, response_json, status=200):
        mock_response = AsyncMock()
        mock_response.status = status
        mock_response.json = AsyncMock(return_value=response_json)
        mock_response.text = AsyncMock(return_value=str(response_json))
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_response)
        return mock_session

    @patch('ingen.utils.app_http.auth.properties')
    def test_fetch_token_client_credentials(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'my_id',
            'api_auth.client_secret': 'my_secret'
        }.get(key)
        mock_session = self._make_mock_session(self.token_response)

        client = OAuth2Client(self.auth_config)
        token = self._run_async(client._fetch_token(mock_session))

        self.assertEqual('test_access_token', token.access_token)
        mock_session.post.assert_called_once()
        call_kwargs = mock_session.post.call_args
        # Verify correct URL
        self.assertEqual('https://auth.example.com/token', call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get('url'))

    @patch('ingen.utils.app_http.auth.properties')
    def test_fetch_token_client_secret_basic(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'my_id',
            'api_auth.client_secret': 'my_secret'
        }.get(key)
        mock_session = self._make_mock_session(self.token_response)

        client = OAuth2Client(self.auth_config)
        self._run_async(client._fetch_token(mock_session))

        call_kwargs = mock_session.post.call_args
        headers = call_kwargs[1].get('headers', {})
        expected_creds = base64.b64encode(b'my_id:my_secret').decode('latin1')
        self.assertEqual(f'Basic {expected_creds}', headers.get('Authorization'))

    @patch('ingen.utils.app_http.auth.properties')
    def test_fetch_token_client_secret_post(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'my_id',
            'api_auth.client_secret': 'my_secret'
        }.get(key)
        config = {**self.auth_config, 'method': 'client_secret_post'}
        mock_session = self._make_mock_session(self.token_response)

        client = OAuth2Client(config)
        self._run_async(client._fetch_token(mock_session))

        call_kwargs = mock_session.post.call_args
        body = call_kwargs[1].get('data', {})
        self.assertEqual('my_id', body.get('client_id'))
        self.assertEqual('my_secret', body.get('client_secret'))
        headers = call_kwargs[1].get('headers', {})
        self.assertNotIn('Authorization', headers)

    @patch('ingen.utils.app_http.auth.properties')
    def test_fetch_token_password_grant(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'my_id',
            'api_auth.client_secret': 'my_secret',
            'api_auth.username': 'john',
            'api_auth.password': 'secret123'
        }.get(key)
        config = {
            **self.auth_config,
            'grant_type': 'password',
        }
        mock_session = self._make_mock_session(self.token_response)

        client = OAuth2Client(config)
        self._run_async(client._fetch_token(mock_session))

        call_kwargs = mock_session.post.call_args
        body = call_kwargs[1].get('data', {})
        self.assertEqual('password', body.get('grant_type'))
        self.assertEqual('john', body.get('username'))
        self.assertEqual('secret123', body.get('password'))

    @patch('ingen.utils.app_http.auth.properties')
    def test_ensure_active_token_caches(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'my_id',
            'api_auth.client_secret': 'my_secret'
        }.get(key)
        mock_session = self._make_mock_session(self.token_response)

        client = OAuth2Client(self.auth_config)
        token1 = self._run_async(client.ensure_active_token(mock_session))
        token2 = self._run_async(client.ensure_active_token(mock_session))

        self.assertEqual(token1.access_token, token2.access_token)
        # Only one POST call - second call uses cache
        mock_session.post.assert_called_once()

    @patch('ingen.utils.app_http.auth.properties')
    def test_ensure_active_token_refetches_on_expiry(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'my_id',
            'api_auth.client_secret': 'my_secret'
        }.get(key)
        expired_response = {**self.token_response, 'expires_in': 0}
        mock_session = self._make_mock_session(expired_response)

        client = OAuth2Client(self.auth_config)
        self._run_async(client.ensure_active_token(mock_session))
        self._run_async(client.ensure_active_token(mock_session))

        # Two POST calls - token expired, so it was re-fetched
        self.assertEqual(2, mock_session.post.call_count)

    @patch('ingen.utils.app_http.auth.properties')
    def test_ensure_active_token_uses_refresh_token(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'my_id',
            'api_auth.client_secret': 'my_secret'
        }.get(key)
        # First response includes refresh_token, but expires immediately
        initial_response = {
            'access_token': 'initial_token',
            'expires_in': 0,
            'refresh_token': 'my_refresh_token',
        }
        refresh_response = {
            'access_token': 'refreshed_token',
            'expires_in': 3600,
        }

        # Build mock session that returns different responses on successive calls
        mock_resp_1 = AsyncMock()
        mock_resp_1.status = 200
        mock_resp_1.json = AsyncMock(return_value=initial_response)
        mock_resp_1.__aenter__ = AsyncMock(return_value=mock_resp_1)
        mock_resp_1.__aexit__ = AsyncMock(return_value=False)

        mock_resp_2 = AsyncMock()
        mock_resp_2.status = 200
        mock_resp_2.json = AsyncMock(return_value=refresh_response)
        mock_resp_2.__aenter__ = AsyncMock(return_value=mock_resp_2)
        mock_resp_2.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.post = MagicMock(side_effect=[mock_resp_1, mock_resp_2])

        config = {**self.auth_config, 'grant_type': 'password'}
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'my_id', 'api_auth.client_secret': 'my_secret',
            'api_auth.username': 'john', 'api_auth.password': 'pass'
        }.get(key)

        client = OAuth2Client(config)
        self._run_async(client.ensure_active_token(mock_session))
        token = self._run_async(client.ensure_active_token(mock_session))

        self.assertEqual('refreshed_token', token.access_token)
        self.assertEqual(2, mock_session.post.call_count)
        # Second call should be a refresh_token grant
        second_call = mock_session.post.call_args_list[1]
        body = second_call[1].get('data', {})
        self.assertEqual('refresh_token', body.get('grant_type'))
        self.assertEqual('my_refresh_token', body.get('refresh_token'))

    @patch('ingen.utils.app_http.auth.properties')
    def test_token_endpoint_error(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'my_id',
            'api_auth.client_secret': 'my_secret'
        }.get(key)
        mock_session = self._make_mock_session({}, status=401)

        client = OAuth2Client(self.auth_config)
        with self.assertRaises(ConnectionError):
            self._run_async(client._fetch_token(mock_session))

    @patch('ingen.utils.app_http.auth.properties')
    def test_refresh_token_fallback_on_failure(self, mock_properties):
        """When refresh fails (non-200), should fall back to _fetch_token."""
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'my_id', 'api_auth.client_secret': 'my_secret',
            'api_auth.username': 'john', 'api_auth.password': 'pass'
        }.get(key)

        # First call: fetch returns token with refresh_token, expires immediately
        initial_response = {
            'access_token': 'initial_token',
            'expires_in': 0,
            'refresh_token': 'my_refresh_token',
        }
        # Second call: refresh fails with 401
        refresh_fail = AsyncMock()
        refresh_fail.status = 401
        refresh_fail.text = AsyncMock(return_value='refresh denied')
        refresh_fail.__aenter__ = AsyncMock(return_value=refresh_fail)
        refresh_fail.__aexit__ = AsyncMock(return_value=False)

        # Third call: fallback re-fetch succeeds
        refetch_response = {
            'access_token': 'new_token',
            'expires_in': 3600,
        }
        mock_resp_1 = AsyncMock()
        mock_resp_1.status = 200
        mock_resp_1.json = AsyncMock(return_value=initial_response)
        mock_resp_1.__aenter__ = AsyncMock(return_value=mock_resp_1)
        mock_resp_1.__aexit__ = AsyncMock(return_value=False)

        mock_resp_3 = AsyncMock()
        mock_resp_3.status = 200
        mock_resp_3.json = AsyncMock(return_value=refetch_response)
        mock_resp_3.__aenter__ = AsyncMock(return_value=mock_resp_3)
        mock_resp_3.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.post = MagicMock(side_effect=[mock_resp_1, refresh_fail, mock_resp_3])

        config = {**self.auth_config, 'grant_type': 'password'}
        client = OAuth2Client(config)
        # First call fetches initial token
        self._run_async(client.ensure_active_token(mock_session))
        # Second call: token expired, has refresh_token -> tries refresh -> fails -> falls back to fetch
        token = self._run_async(client.ensure_active_token(mock_session))

        self.assertEqual('new_token', token.access_token)
        self.assertEqual(3, mock_session.post.call_count)

    @patch('ingen.utils.app_http.auth.properties')
    def test_scope_passed_in_token_request(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'my_id',
            'api_auth.client_secret': 'my_secret'
        }.get(key)
        mock_session = self._make_mock_session(self.token_response)

        client = OAuth2Client(self.auth_config)
        self._run_async(client._fetch_token(mock_session))

        call_kwargs = mock_session.post.call_args
        body = call_kwargs[1].get('data', {})
        self.assertEqual('read', body.get('scope'))

    @patch('ingen.utils.app_http.auth.properties')
    def test_scope_as_array_joined_with_spaces(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'my_id',
            'api_auth.client_secret': 'my_secret'
        }.get(key)
        config = {
            **self.auth_config,
            'scope': ['read', 'write', 'admin'],
        }
        mock_session = self._make_mock_session(self.token_response)

        client = OAuth2Client(config)
        self._run_async(client._fetch_token(mock_session))

        call_kwargs = mock_session.post.call_args
        body = call_kwargs[1].get('data', {})
        self.assertEqual('read write admin', body.get('scope'))

    @patch('ingen.utils.app_http.auth.properties')
    def test_default_auth_method_is_client_secret_basic(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'my_id',
            'api_auth.client_secret': 'my_secret'
        }.get(key)
        # Config without method specified - should default to client_secret_basic
        config = {
            'type': 'OAuth2',
            'grant_type': 'client_credentials',
            'token_url': 'https://auth.example.com/token',
        }
        mock_session = self._make_mock_session(self.token_response)

        client = OAuth2Client(config)
        self._run_async(client._fetch_token(mock_session))

        call_kwargs = mock_session.post.call_args
        headers = call_kwargs[1].get('headers', {})
        self.assertIn('Authorization', headers)
        self.assertTrue(headers['Authorization'].startswith('Basic '))

    @patch('ingen.utils.app_http.auth.properties')
    def test_missing_required_config_raises(self, mock_properties):
        mock_properties.get_property.return_value = 'value'
        config = {
            'type': 'OAuth2',
            'grant_type': 'client_credentials',
            # missing token_url
        }
        with self.assertRaises(ValueError) as ctx:
            OAuth2Client(config)
        self.assertIn('token_url', str(ctx.exception))


class TestGetAuth(unittest.TestCase):

    def setUp(self):
        _oauth2_clients.clear()

    def _run_async(self, coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def test_none_auth_config(self):
        result = self._run_async(get_auth(None, None))
        self.assertIsNone(result.auth)
        self.assertEqual({}, result.headers)

    @patch('ingen.utils.app_http.auth.properties')
    def test_basic_auth_dispatch(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: 'value'
        result = self._run_async(get_auth(None, {'type': 'BasicAuth'}))
        self.assertIsInstance(result.auth, BasicAuth)

    @patch('ingen.utils.app_http.auth.properties')
    def test_oauth2_pre_obtained_dispatch(self, mock_properties):
        mock_properties.get_property.return_value = 'static_token'
        auth_config = {
            'type': 'OAuth2',
            'grant_type': 'token',
        }
        result = self._run_async(get_auth(None, auth_config))
        self.assertEqual({'Authorization': 'Bearer static_token'}, result.headers)

    @patch('ingen.utils.app_http.auth.properties')
    def test_oauth2_client_credentials_dispatch(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'id', 'api_auth.client_secret': 'secret'
        }.get(key)

        token_response = {'access_token': 'cc_token', 'expires_in': 3600}
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=token_response)
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=False)
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_resp)

        auth_config = {
            'type': 'OAuth2',
            'grant_type': 'client_credentials',
            'token_url': 'https://auth.example.com/token',
        }
        result = self._run_async(get_auth(mock_session, auth_config))
        self.assertEqual({'Authorization': 'Bearer cc_token'}, result.headers)
        self.assertIsNone(result.auth)

    @patch('ingen.utils.app_http.auth.properties')
    def test_oauth2_password_dispatch(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key: {
            'api_auth.client_id': 'id', 'api_auth.client_secret': 'secret',
            'api_auth.username': 'john', 'api_auth.password': 'pass123'
        }.get(key)

        token_response = {'access_token': 'pw_token', 'expires_in': 3600}
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=token_response)
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=False)
        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_resp)

        auth_config = {
            'type': 'OAuth2',
            'grant_type': 'password',
            'token_url': 'https://auth.example.com/token',
        }
        result = self._run_async(get_auth(mock_session, auth_config))
        self.assertEqual({'Authorization': 'Bearer pw_token'}, result.headers)
        # Verify username/password were sent in the POST body
        call_kwargs = mock_session.post.call_args
        body = call_kwargs[1].get('data', {})
        self.assertEqual('password', body.get('grant_type'))
        self.assertEqual('john', body.get('username'))
        self.assertEqual('pass123', body.get('password'))

    def test_unsupported_auth_type(self):
        with self.assertRaises(ValueError):
            self._run_async(get_auth(None, {'type': 'UnknownAuth'}))

    def test_unsupported_grant_type(self):
        with self.assertRaises(ValueError):
            self._run_async(get_auth(None, {'type': 'OAuth2', 'grant_type': 'implicit'}))


if __name__ == '__main__':
    unittest.main()
