from __future__ import annotations

from typing import Any, overload
import httpx
from inline_snapshot import Snapshot

from .._models import Headers, Request, Response
from .._serializer import snapshot_to_internal
from .._typing import assert_never


@overload
def httpx_to_internal(
    model: httpx.Request,
) -> Request: ...


@overload
def httpx_to_internal(
    model: httpx.Response,
) -> Response: ...


def httpx_to_internal(
    model: httpx.Request | httpx.Response,
) -> Request | Response:
    if isinstance(model, httpx.Request):
        return Request(
            method=model.method,
            url=str(model.url),
            headers=Headers(model.headers),
            body=model.content,
        )
    elif isinstance(model, httpx.Response):
        model.aiter_bytes
        return Response(
            status_code=model.status_code,
            headers=Headers(model.headers),
            body=model.content,
        )
    else:
        assert_never(model, "Unsupported model type for serialization")


def internal_to_httpx(model: Response) -> httpx.Response:
    return httpx.Response(
        status_code=model.status_code,
        headers=model.headers,
        content=model.body,
    )


class AsyncSnapshotTransport(httpx.AsyncBaseTransport, httpx.BaseTransport):
    def __init__(
        self,
        next_transport: httpx.AsyncBaseTransport,
        snapshot: Snapshot[list[dict[str, Any]]],
        is_recording: bool,
    ) -> None:
        self.is_recording = is_recording
        self.next_transport = next_transport
        self.collected_pairs: list[tuple[Request, Response]] = []
        self.snapshot = snapshot
        self._request_number = -1

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self._request_number += 1

        if self.is_recording:
            # In live mode, we would normally send the request to the server.
            response = await self.next_transport.handle_async_request(request)
            await response.aread()
            self.collected_pairs.append(
                (httpx_to_internal(request), httpx_to_internal(response))
            )
        else:
            internal = snapshot_to_internal(self.snapshot)
            response = internal_to_httpx(internal[self._request_number])
        return response


class SyncSnapshotTransport(httpx.AsyncBaseTransport, httpx.BaseTransport):
    def __init__(
        self,
        next_transport: httpx.BaseTransport,
        snapshot: Snapshot[list[dict[str, Any]]],
        is_recording: bool,
    ) -> None:
        self.is_recording = is_recording
        self.next_transport = next_transport
        self.collected_pairs: list[tuple[Request, Response]] = []
        self.snapshot = snapshot
        self._request_number = -1

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self._request_number += 1

        if self.is_recording:
            # In live mode, we would normally send the request to the server.
            response = self.next_transport.handle_request(request)
            response.read()
            self.collected_pairs.append(
                (httpx_to_internal(request), httpx_to_internal(response))
            )
        else:
            internal = snapshot_to_internal(self.snapshot)
            response = internal_to_httpx(internal[self._request_number])
        return response
