from typing import Any, Iterator, cast
import warnings
import httpx
import pytest
import inline_snapshot

from ._serializer import SnapshotSerializerOptions, internal_to_snapshot


__all__ = [
    "snapshot_requests_session",
    "snapshot_async_httpx_client",
    "snapshot_sync_httpx_client",
    "http_snapshot_serializer_options",
    "is_recording",
]


@pytest.fixture
def is_recording(request: pytest.FixtureRequest) -> bool:
    try:
        return cast(bool, request.config.getoption("--http-record"))
    except Exception:
        return False


try:
    import httpx

    @pytest.fixture
    def snapshot_async_httpx_client(
        http_snapshot: inline_snapshot.Snapshot[Any],
        http_snapshot_serializer_options: SnapshotSerializerOptions,
        is_recording: bool,
    ) -> Iterator[httpx.AsyncClient]:
        warnings.warn(
            "snapshot_async_httpx_client fixture is deprecated. "
            "Use HttpxAsyncSnapshotClient context manager instead: "
            "async with HttpxAsyncSnapshotClient(snapshot=http_snapshot, is_recording=is_recording) as client: ...",
            DeprecationWarning,
            stacklevel=2,
        )
        from ._integrations._httpx import AsyncSnapshotTransport

        snapshot_transport = AsyncSnapshotTransport(
            httpx.AsyncHTTPTransport(),
            http_snapshot,
            is_recording=is_recording,
        )

        try:
            yield httpx.AsyncClient(
                transport=snapshot_transport,
            )

            if snapshot_transport.is_recording:
                assert (
                    internal_to_snapshot(
                        snapshot_transport.collected_pairs,
                        http_snapshot_serializer_options,
                    )
                    == snapshot_transport.snapshot
                )
        finally:
            pass

    @pytest.fixture
    def snapshot_sync_httpx_client(
        http_snapshot: inline_snapshot.Snapshot[Any],
        http_snapshot_serializer_options: SnapshotSerializerOptions,
        is_recording: bool,
    ) -> Iterator[httpx.Client]:
        warnings.warn(
            "snapshot_sync_httpx_client fixture is deprecated. "
            "Use HttpxSyncSnapshotClient context manager instead: "
            "with HttpxSyncSnapshotClient(snapshot=http_snapshot, is_recording=is_recording) as client: ...",
            DeprecationWarning,
            stacklevel=2,
        )
        if httpx is None:
            raise ImportError(
                "httpx is not installed. Please install http-snapshot with httpx feature [pip install http-snapshot[httpx]]"
            )
        from ._integrations._httpx import SyncSnapshotTransport

        snapshot_transport = SyncSnapshotTransport(
            httpx.HTTPTransport(),
            http_snapshot,
            is_recording=is_recording,
        )
        try:
            yield httpx.Client(
                transport=snapshot_transport,
            )

            if snapshot_transport.is_recording:
                assert (
                    internal_to_snapshot(
                        snapshot_transport.collected_pairs,
                        http_snapshot_serializer_options,
                    )
                    == snapshot_transport.snapshot
                )
        finally:
            snapshot_transport.close()
except ImportError:

    @pytest.fixture
    def snapshot_async_httpx_client(
        http_snapshot: inline_snapshot.Snapshot[Any],
        http_snapshot_serializer_options: SnapshotSerializerOptions,
        is_recording: bool,
    ) -> Iterator[Any]:
        raise ImportError(
            "httpx is not installed. Please install http-snapshot with httpx feature [pip install http-snapshot[httpx]]"
        )

    @pytest.fixture
    def snapshot_sync_httpx_client(
        http_snapshot: inline_snapshot.Snapshot[Any],
        http_snapshot_serializer_options: SnapshotSerializerOptions,
        is_recording: bool,
    ) -> Iterator[httpx.Client]:
        raise ImportError(
            "httpx is not installed. Please install http-snapshot with httpx feature [pip install http-snapshot[httpx]]"
        )


try:
    import requests

    @pytest.fixture
    def snapshot_requests_session(
        http_snapshot: inline_snapshot.Snapshot[Any],
        http_snapshot_serializer_options: SnapshotSerializerOptions,
        is_recording: bool,
    ) -> Iterator[requests.Session]:
        warnings.warn(
            "snapshot_requests_session fixture is deprecated. "
            "Use RequestsSnapshotSession context manager instead: "
            "with RequestsSnapshotSession(snapshot=http_snapshot, is_recording=is_recording) as session: ...",
            DeprecationWarning,
            stacklevel=2,
        )
        from ._integrations._requests import SnapshotAdapter

        with requests.Session() as session:
            adapter = SnapshotAdapter(snapshot=http_snapshot, is_recording=is_recording)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            yield session

            if adapter.is_recording:
                assert (
                    internal_to_snapshot(
                        adapter.collected_pairs, http_snapshot_serializer_options
                    )
                    == adapter.snapshot
                )

except ImportError:

    @pytest.fixture
    def snapshot_requests_session(
        http_snapshot: inline_snapshot.Snapshot[Any],
        http_snapshot_serializer_options: SnapshotSerializerOptions,
        is_recording: bool,
    ) -> Iterator[Any]:
        raise ImportError(
            "requests is not installed. Please install http-snapshot with requests feature [pip install http-snapshot[requests]]"
        )


@pytest.fixture
def http_snapshot_serializer_options() -> SnapshotSerializerOptions:
    return SnapshotSerializerOptions()
