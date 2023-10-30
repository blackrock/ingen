#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging
import sys

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def init_logging():
    """Initializes root logger"""

    log = logging.getLogger()
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler(sys.stdout))
    for handler in log.handlers:
        log_formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(log_formatter)
