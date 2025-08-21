from dataclasses import dataclass
from typing import Iterator, List, Mapping, Optional, Union


class Headers(Mapping[str, str]):
    def __init__(self, headers: Mapping[str, Union[str, List[str]]]) -> None:
        self._headers = {
            k.lower(): ([v] if isinstance(v, str) else v[:]) for k, v in headers.items()
        }

    def get_list(self, key: str) -> Optional[List[str]]:
        return self._headers.get(key.lower(), None)

    def __getitem__(self, key: str) -> str:
        return ", ".join(self._headers[key.lower()])

    def __setitem__(self, key: str, value: str) -> None:
        self._headers.setdefault(key.lower(), []).append(value)

    def __delitem__(self, key: str) -> None:
        del self._headers[key.lower()]

    def __iter__(self) -> Iterator[str]:
        return iter(self._headers)

    def __len__(self) -> int:
        return len(self._headers)

    def __eq__(self, other_headers: object) -> bool:
        if not isinstance(other_headers, Headers):
            return False
        return self._headers == other_headers._headers


@dataclass
class Request:
    method: str
    url: str
    headers: Headers
    body: bytes


@dataclass
class Response:
    status_code: int
    headers: Headers
    body: bytes
