from dataclasses import dataclass
from typing import Mapping


@dataclass
class Request:
    method: str
    url: str
    headers: Mapping[str, str]
    body: bytes


@dataclass
class Response:
    status_code: int
    headers: Mapping[str, str]
    body: bytes
