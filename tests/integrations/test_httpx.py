from typing import Any

import inline_snapshot
import pytest

from http_snapshot._serializer import SnapshotSerializerOptions
from http_snapshot.httpx import HttpxAsyncSnapshotClient, HttpxSyncSnapshotClient


@pytest.mark.anyio
@pytest.mark.parametrize(
    "http_snapshot",
    [inline_snapshot.external("uuid:01c2382a-2b15-45bd-8f4e-f012b5bfebaa.json")],
)
async def test_basic_snapshot(
    http_snapshot: inline_snapshot.Snapshot[Any],
    http_snapshot_serializer_options: SnapshotSerializerOptions,
    is_recording: bool,
) -> None:
    async with HttpxAsyncSnapshotClient(
        snapshot=http_snapshot,
        is_recording=is_recording,
    ) as client:
        await client.get("https://hishel.com")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "http_snapshot, http_snapshot_serializer_options",
    [
        (
            inline_snapshot.external("uuid:f50614e8-25ff-460a-a2f2-4693c4d37abb.json"),
            SnapshotSerializerOptions(exclude_request_headers=["X-Secret-Key"]),
        ),
    ],
)
async def test_with_excluded_request_header(
    http_snapshot: inline_snapshot.Snapshot[Any],
    http_snapshot_serializer_options: SnapshotSerializerOptions,
    is_recording: bool,
) -> None:
    async with HttpxAsyncSnapshotClient(
        snapshot=http_snapshot,
        is_recording=is_recording,
    ) as client:
        await client.get(
            "https://jsonplaceholder.typicode.com/todos/1",
            headers={"X-Secret-Key": "secret"},
        )


@pytest.mark.parametrize(
    "http_snapshot",
    [inline_snapshot.external("uuid:55be68a6-0264-48c5-9caa-d243f3361b89.json")],
)
def test_basic_sync_snapshot(
    http_snapshot: inline_snapshot.Snapshot[Any],
    http_snapshot_serializer_options: SnapshotSerializerOptions,
    is_recording: bool,
) -> None:
    with HttpxSyncSnapshotClient(
        snapshot=http_snapshot,
        is_recording=is_recording,
    ) as client:
        resp = client.get("https://hishel.com")

    assert resp.status_code == 200


@pytest.mark.parametrize(
    "http_snapshot, http_snapshot_serializer_options",
    [
        (
            inline_snapshot.external("uuid:1d61a99b-2d56-48f3-889d-8e9b0c5b70c3.json"),
            SnapshotSerializerOptions(exclude_request_headers=["X-Secret-Key"]),
        ),
    ],
)
def test_sync_with_excluded_request_header(
    http_snapshot: inline_snapshot.Snapshot[Any],
    http_snapshot_serializer_options: SnapshotSerializerOptions,
    is_recording: bool,
) -> None:
    with HttpxSyncSnapshotClient(
        snapshot=http_snapshot,
        is_recording=is_recording,
    ) as client:
        client.get(
            "https://jsonplaceholder.typicode.com/todos/1",
            headers={"X-Secret-Key": "secret"},
        )
