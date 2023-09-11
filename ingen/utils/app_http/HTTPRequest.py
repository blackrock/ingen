#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from dataclasses import dataclass
from typing import Optional


@dataclass
class HTTPRequest:
    """Class for HTTP Request data"""
    url: str
    method: str
    headers: Optional[dict] = None
    auth: Optional[dict] = None
    data: Optional[str] = None
