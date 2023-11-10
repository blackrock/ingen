#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import asyncio
import logging
from collections import namedtuple

from aiohttp import ClientSession

from ingen.utils.app_http.success_criterias import status_criteria, DEFAULT_STATUS_CRITERIA_OPTIONS

logger = logging.getLogger()

HTTPResponse = namedtuple('HTTPResponse', ['status', 'headers', 'data'])


async def http_retry_request(
        session: ClientSession,
        method,
        url,
        retries=2,
        interval=1,
        interval_increment=2,
        success_criteria=status_criteria,
        criteria_options=DEFAULT_STATUS_CRITERIA_OPTIONS,
        **kwargs):
    """
    Asynchronously retries the HTTP call until the given success_criteria (a callable) is succeeded or
    number of retries reaches to zero
    :param session: aiohttp ClientSession
    :param method: HTTP Methods
    :param url: Request URL
    :param retries: How many times to retry
    :param interval: How long to wait before retrying (in seconds)
    :param interval_increment: Number of seconds added to interval when retrying.
                               So if a request fails with following params:
                               retires = 4, interval = 2, interval_increment = 2
                               4 retries will be made after 2, 4, 6, and 8 seconds.
    :param success_criteria: a callable that defines the success_criteria,
                             see 'src.utils.app_http.success_criterias.py' for more
    :param criteria_options: dict-like options required by success_criteria method
    :param kwargs: additional kwargs for HTTP methods, eg., headers, auth, data etc
    :return: If successful, returns a namedtuple HTTPResponse containing response status, headers and body,
             otherwise None
    """

    _method = method.lower()
    if _method not in ["get", "post", "put", "patch", "delete"]:
        raise ValueError("Unsupported HTTP method passed for retry")

    attempt = retries + 1
    should_retry = None

    while attempt != 0:
        attempt -= 1
        wait_time = interval
        if should_retry:
            wait_time = wait_time + interval_increment
            await asyncio.sleep(wait_time)
        async with getattr(session, _method)(url, **kwargs) as response:
            logger.info(f"awaiting {_method.upper()} {url}")

            try:
                status = response.status
                headers = response.headers

                if headers.get('Content-Type') and 'application/json' in headers.get('Content-Type', ''):
                    data = await response.json()
                else:
                    data = await response.text()
            except Exception as e:
                raise ConnectionError(f"Error occurred while getting response from url {url}: {e}")

            http_response = HTTPResponse(status, headers, data)
            logger.info(f"Response for {url}: {http_response}")

            if success_criteria(http_response, criteria_options):
                return http_response

            should_retry = True
            logger.info(f"Retrying in {wait_time} seconds")

    logger.error(f"Could not get a successful response for url: {url} after {retries} retries.")
