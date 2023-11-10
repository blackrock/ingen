#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import asyncio
import logging
from asyncio import CancelledError

import aiohttp
from aiohttp import ClientSession, BasicAuth

from ingen.utils.app_http.aiohttp_retry import http_retry_request, HTTPResponse
from ingen.utils.app_http.success_criterias import status_criteria, DEFAULT_STATUS_CRITERIA_OPTIONS
from ingen.utils.properties import Properties

log = logging.getLogger()


def execute_requests(requests, request_params):
    """
    Asynch execution of requests
    :param requests:        list of HTTPRequests
    :param request_params:  additional config parameters for app_http request like retries, intervals, etc
    :return: list of response body
    """
    http_responses = asyncio.run(execute(requests, request_params))
    log.info(f"responses length: {len(http_responses)}")
    data = list(map(lambda res: res.data, filter(lambda res: type(res) is HTTPResponse, http_responses)))
    log.info(f"data len after filtering errors: {len(data)}")
    failed_responses = list((filter(lambda res: type(res) is not HTTPResponse, http_responses)))
    log.error(f"{len(failed_responses)} error in app_http responses: {failed_responses}")
    if failed_responses and not request_params.get('ignore_failure', True):
        raise Exception("Failure in executing requests.")
    return data


async def execute(requests, request_params):
    request_params['size'] = len(requests)
    log.info(f"Starting to process {len(requests)} requests")
    results = []
    queue = asyncio.Queue(maxsize=request_params.get('queue_size', 1))
    ssl = request_params.get('ssl', True)
    if not ssl:
        log.warning("SSL is turned off")
    connector = aiohttp.TCPConnector(ssl=request_params.get('ssl', True))

    async with ClientSession(connector=connector) as session:
        # producer
        fill_task = asyncio.create_task(fill_queue(requests, queue))
        # consumers
        tasks = []
        tasks_len = request_params.get('tasks_len', 1)
        log.info(f"PROC TASK: Creating {tasks_len} tasks to process queue")
        for _ in range(tasks_len):
            tasks.append(
                asyncio.create_task(fetch(session, queue, request_params, results))
            )

        # wait for the producers to finish
        await asyncio.gather(fill_task)

        # wait for the remaining task to be processed
        await queue.join()

        # cancel the consumers
        for task in tasks:
            task.cancel()

    return results


async def fill_queue(requests, queue):
    log.info("FILL TASK: Starting to fill request queue with requests")
    while len(requests) > 0:
        await queue.put(requests.pop())


async def fetch(session, queue, request_params, results):
    """
    Consumer method that is responsible for fetching requests from queue and executing them.
    :param session: aiohttp.ClientSession
    :param queue: asyncio.Queue
    :param request_params: additional config parameters for app_http request like retries, intervals, etc.
    :param results: list of response body
    :return: None
    """
    while True:
        try:
            request = await queue.get()
            response = await http_retry_request(session,
                                                request.method,
                                                request.url,
                                                retries=request_params.get('retries', 2),
                                                interval=request_params.get('interval', 1),
                                                interval_increment=request_params.get('interval_increment', 2),
                                                success_criteria=request_params.get('success_criteria',
                                                                                    status_criteria),
                                                criteria_options=request_params.get('criteria_options',
                                                                                    DEFAULT_STATUS_CRITERIA_OPTIONS),
                                                auth=api_auth(request.auth),
                                                headers=request.headers,
                                                data=request.data)
        except CancelledError:
            log.info("Task cancelled.")
            break
        except Exception as e:
            log.exception(f"Error in fetch task:  {e}")
            queue.task_done()
        else:
            results.append(response)
            log.info(f"Processed request {len(results)} / {request_params.get('size')}")
            queue.task_done()


def api_auth(auth):
    """
    Method responsible for authenticating API. aiohttp.BasicAuth is used for it.
    :param auth: Dictionary that contains auth.type, auth.username and auth.pwd.
    :return: aiohttp.BasicAuth if auth.type is BasicAuth, None otherwise.
    """
    if auth and auth.get('type') == 'BasicAuth':
        try:
            user = Properties.get_property('api_auth.username')
            password = Properties.get_property('api_auth.password')
            return BasicAuth(user, password)
        except Exception as e:
            log.exception(f"Error while getting the property username/pwd for api call: {e} ")
