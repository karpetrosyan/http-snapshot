from __future__ import annotations

from typing import Any, Mapping, overload
from inline_snapshot import Snapshot
from requests.adapters import HTTPAdapter
from requests.models import PreparedRequest, Response
from http_snapshot._models import Headers, Request, Response as InternalResponse
from http_snapshot._serializer import snapshot_to_internal
from urllib3.util.retry import Retry as Retry
from http_snapshot._typing import assert_never


@overload
def requests_to_internal(
    model: PreparedRequest,
) -> Request: ...


@overload
def requests_to_internal(
    model: Response,
) -> InternalResponse: ...


def requests_to_internal(
    model: PreparedRequest | Response,
) -> Request | InternalResponse:
    if isinstance(model, PreparedRequest):
        body: bytes
        if isinstance(model.body, str):
            body = model.body.encode("utf-8")
        elif isinstance(model.body, bytes):
            body = model.body
        else:
            body = b""
        assert model.method
        return Request(
            method=model.method,
            url=str(model.url),
            headers=Headers(model.headers),
            body=body,
        )
    elif isinstance(model, Response):
        content = model.content
        if not isinstance(content, bytes):
            raise RuntimeError(
                f"Expected response content to be bytes, got {type(content).__name__}"
            )
        return InternalResponse(
            status_code=model.status_code,
            headers=Headers(model.headers),
            body=content,
        )
    else:
        assert_never(model, "Unsupported model type for serialization")
    raise RuntimeError(
        "This line should never be reached, but is here to satisfy type checkers."
    )


def internal_to_requests(model: InternalResponse, adapter: HTTPAdapter) -> Response:
    response = Response()

    response.status_code = model.status_code
    for key, value in model.headers.items():
        response.headers[key] = value
    response._content = model.body
    return response


class SnapshotAdapter(HTTPAdapter):
    """
    A custom HTTPAdapter that can be used with requests to capture HTTP interactions
    for snapshot testing.
    """

    def __init__(
        self,
        snapshot: Snapshot[list[dict[str, Any]]],
        pool_connections: int = 10,
        pool_maxsize: int = 10,
        max_retries: Retry | int | None = 0,
        pool_block: bool = False,
        is_recording: bool = False,
    ) -> None:
        super().__init__(pool_connections, pool_maxsize, max_retries, pool_block)
        self.snapshot = snapshot
        self.is_recording = is_recording
        self.collected_pairs: list[tuple[Request, InternalResponse]] = []
        self._request_number = -1

    def send(
        self,
        request: PreparedRequest,
        stream: bool = False,
        timeout: None | float | tuple[float, float] | tuple[float, None] = None,
        verify: bool | str = True,
        cert: None | bytes | str | tuple[bytes | str, bytes | str] = None,
        proxies: Mapping[str, str] | None = None,
    ) -> Response:
        self._request_number += 1

        if self.is_recording:
            response = super().send(request, False, timeout, verify, cert, proxies)
            self.collected_pairs.append(
                (requests_to_internal(request), requests_to_internal(response))
            )
        else:
            internal = snapshot_to_internal(self.snapshot)
            response = internal_to_requests(internal[self._request_number], self)

        return response
