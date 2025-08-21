import os
from typing import Any, Iterator
import httpx
import pytest
import inline_snapshot

from ._serializer import SnapshotSerializerOptions, internal_to_snapshot


try:
    import httpx
except ImportError:
    httpx: Any = None

try:
    import requests
except ImportError:
    requests: Any = None


def is_live() -> bool:
    return os.getenv("HTTP_SNAPSHOT_LIVE") == "1"


@pytest.fixture
def http_snapshot_serializer_options() -> SnapshotSerializerOptions:
    return SnapshotSerializerOptions()


@pytest.fixture
def snapshot_httpx_client(
    http_snapshot: inline_snapshot.Snapshot[Any],
    http_snapshot_serializer_options: SnapshotSerializerOptions,
) -> Iterator[httpx.AsyncClient]:
    if httpx is None:
        raise ImportError(
            "httpx is not installed. Please install http-snapshot with httpx feature [pip install http-snapshot[httpx]]"
        )
    from ._integrations._httpx import SnapshotTransport

    snapshot_transport = SnapshotTransport(
        httpx.AsyncHTTPTransport(),
        http_snapshot,
        is_live=is_live(),
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
def snapshot_requests_session(
    http_snapshot: inline_snapshot.Snapshot[Any],
    http_snapshot_serializer_options: SnapshotSerializerOptions,
) -> Iterator[requests.Session]:
    if requests is None:
        raise ImportError(
            "requests is not installed. Please install http-snapshot with requests feature [pip install http-snapshot[requests]]"
        )

    from ._integrations._requests import SnapshotAdapter

    with requests.Session() as session:
        adapter = SnapshotAdapter(snapshot=http_snapshot, is_live=is_live())
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
