from typing import Any, Iterator
import httpx
import pytest
import inline_snapshot

from ._serializer import SnapshotSerializerOptions, internal_to_snapshot


try:
    import httpx

    @pytest.fixture
    def snapshot_async_httpx_client(
        http_snapshot: inline_snapshot.Snapshot[Any],
        http_snapshot_serializer_options: SnapshotSerializerOptions,
        is_live: bool,
    ) -> Iterator[httpx.AsyncClient]:
        from ._integrations._httpx import AsyncSnapshotTransport

        snapshot_transport = AsyncSnapshotTransport(
            httpx.AsyncHTTPTransport(),
            http_snapshot,
            is_live=is_live,
        )
        yield httpx.AsyncClient(
            transport=snapshot_transport,
        )

        if snapshot_transport.is_live:
            assert (
                internal_to_snapshot(
                    snapshot_transport.collected_pairs, http_snapshot_serializer_options
                )
                == snapshot_transport.snapshot
            )

    @pytest.fixture
    def snapshot_sync_httpx_client(
        http_snapshot: inline_snapshot.Snapshot[Any],
        http_snapshot_serializer_options: SnapshotSerializerOptions,
        is_live: bool,
    ) -> Iterator[httpx.Client]:
        if httpx is None:
            raise ImportError(
                "httpx is not installed. Please install http-snapshot with httpx feature [pip install http-snapshot[httpx]]"
            )
        from ._integrations._httpx import SyncSnapshotTransport

        snapshot_transport = SyncSnapshotTransport(
            httpx.HTTPTransport(),
            http_snapshot,
            is_live=is_live,
        )
        yield httpx.Client(
            transport=snapshot_transport,
        )

        if snapshot_transport.is_live:
            assert (
                internal_to_snapshot(
                    snapshot_transport.collected_pairs, http_snapshot_serializer_options
                )
                == snapshot_transport.snapshot
            )
except ImportError:

    @pytest.fixture
    def snapshot_async_httpx_client(
        http_snapshot: inline_snapshot.Snapshot[Any],
        http_snapshot_serializer_options: SnapshotSerializerOptions,
        is_live: bool,
    ) -> Iterator[Any]:
        raise ImportError(
            "httpx is not installed. Please install http-snapshot with httpx feature [pip install http-snapshot[httpx]]"
        )

    @pytest.fixture
    def snapshot_sync_httpx_client(
        http_snapshot: inline_snapshot.Snapshot[Any],
        http_snapshot_serializer_options: SnapshotSerializerOptions,
        is_live: bool,
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
        is_live: bool,
    ) -> Iterator[requests.Session]:
        from ._integrations._requests import SnapshotAdapter

        with requests.Session() as session:
            adapter = SnapshotAdapter(snapshot=http_snapshot, is_live=is_live)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            yield session

            if adapter.is_live:
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
        is_live: bool,
    ) -> Iterator[Any]:
        raise ImportError(
            "requests is not installed. Please install http-snapshot with requests feature [pip install http-snapshot[requests]]"
        )


@pytest.fixture
def is_live(pytestconfig: Any) -> bool:
    if pytestconfig.option.inline_snapshot is None:
        return False
    flags = pytestconfig.option.inline_snapshot.split(",")
    return "fix" in flags or "create" in flags


@pytest.fixture
def http_snapshot_serializer_options() -> SnapshotSerializerOptions:
    return SnapshotSerializerOptions()
