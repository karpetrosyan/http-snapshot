from typing import Any
import httpx
import inline_snapshot
import pytest

from http_snapshot._serializer import SnapshotSerializerOptions


@pytest.mark.anyio
@pytest.mark.parametrize(
    "http_snapshot",
    [inline_snapshot.external("uuid:01c2382a-2b15-45bd-8f4e-f012b5bfebaa.json")],
)
async def test_basic_snapshot(snapshot_httpx_client: httpx.AsyncClient) -> None:
    await snapshot_httpx_client.get("https://hishel.com")


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
    snapshot_httpx_client: httpx.AsyncClient, http_snapshot_serializer_options: Any
) -> None:
    await snapshot_httpx_client.get(
        "https://jsonplaceholder.typicode.com/todos/1",
        headers={"X-Secret-Key": "secret"},
    )
