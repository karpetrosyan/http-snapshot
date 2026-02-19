try:
    import httpx
except ImportError:
    raise ImportError(
        "httpx is not installed. Please install http-snapshot with httpx feature [pip install http-snapshot[httpx]]"
    )

from typing import TYPE_CHECKING, Any, Optional
import inline_snapshot


if TYPE_CHECKING:
    from http_snapshot._integrations._httpx import AsyncSnapshotTransport
    from http_snapshot._integrations._httpx import SyncSnapshotTransport

from ._serializer import SnapshotSerializerOptions, internal_to_snapshot


__all__ = [
    "HttpxAsyncSnapshotClient",
    "HttpxSyncSnapshotClient",
]


class HttpxAsyncSnapshotClient:
    def __init__(
        self,
        snapshot: inline_snapshot.Snapshot[list[dict[str, Any]]],
        is_recording: bool,
        serializer_options: Optional[SnapshotSerializerOptions] = None,
        base_transport: Optional[httpx.AsyncBaseTransport] = None,
    ):
        self.snapshot = snapshot
        self.is_recording = is_recording
        self.serializer_options = serializer_options or SnapshotSerializerOptions()
        self.base_transport = base_transport or httpx.AsyncHTTPTransport()
        self._client: Optional[httpx.AsyncClient] = None
        self._transport: Optional["AsyncSnapshotTransport"] = None

    async def __aenter__(self) -> httpx.AsyncClient:
        from ._integrations._httpx import AsyncSnapshotTransport

        self._transport = AsyncSnapshotTransport(
            self.base_transport,
            self.snapshot,
            is_recording=self.is_recording,
        )

        self._client = httpx.AsyncClient(transport=self._transport)
        return self._client

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            if self._transport and self._transport.is_recording:
                assert (
                    internal_to_snapshot(
                        self._transport.collected_pairs,
                        self.serializer_options,
                    )
                    == self._transport.snapshot
                )
        finally:
            if self._client:
                await self._client.aclose()
            if self._transport:
                await self._transport.aclose()
            await self.base_transport.aclose()


class HttpxSyncSnapshotClient:
    def __init__(
        self,
        snapshot: inline_snapshot.Snapshot[list[dict[str, Any]]],
        is_recording: bool,
        serializer_options: Optional[SnapshotSerializerOptions] = None,
        base_transport: Optional[httpx.BaseTransport] = None,
    ):
        self.snapshot = snapshot
        self.is_recording = is_recording
        self.serializer_options = serializer_options or SnapshotSerializerOptions()
        self.base_transport = base_transport or httpx.HTTPTransport()
        self._client: Optional[httpx.Client] = None
        self._transport: Optional["SyncSnapshotTransport"] = None

    def __enter__(self) -> httpx.Client:
        from ._integrations._httpx import SyncSnapshotTransport

        self._transport = SyncSnapshotTransport(
            self.base_transport,
            self.snapshot,
            is_recording=self.is_recording,
        )

        self._client = httpx.Client(transport=self._transport)
        return self._client

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            if self._transport and self._transport.is_recording:
                assert (
                    internal_to_snapshot(
                        self._transport.collected_pairs,
                        self.serializer_options,
                    )
                    == self._transport.snapshot
                )
        finally:
            if self._client:
                self._client.close()
            if self._transport:
                self._transport.close()
            self.base_transport.close()
