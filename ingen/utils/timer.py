import logging
import time

from functools import wraps

log = logging.getLogger()


def log_time(func):
    """This decorator logs the execution time for the decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        log.info(f"Successfully ran function={func.__name__} in time={round(end - start, 2)} seconds.")
        return result

    return wrapper
