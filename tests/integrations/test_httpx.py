import httpx
import inline_snapshot
import pytest

from http_snapshot._serializer import SnapshotSerializerOptions


@pytest.mark.anyio
@pytest.mark.parametrize(
    "http_snapshot",
    [inline_snapshot.external("uuid:01c2382a-2b15-45bd-8f4e-f012b5bfebaa.json")],
)
async def test_basic_snapshot(snapshot_async_httpx_client: httpx.AsyncClient) -> None:
    await snapshot_async_httpx_client.get("https://hishel.com")


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
    snapshot_async_httpx_client: httpx.AsyncClient,
) -> None:
    await snapshot_async_httpx_client.get(
        "https://jsonplaceholder.typicode.com/todos/1",
        headers={"X-Secret-Key": "secret"},
    )


@pytest.mark.parametrize(
    "http_snapshot",
    [inline_snapshot.external("uuid:55be68a6-0264-48c5-9caa-d243f3361b89.json")],
)
def test_basic_sync_snapshot(snapshot_sync_httpx_client: httpx.Client) -> None:
    resp = snapshot_sync_httpx_client.get("https://hishel.com")

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
    snapshot_sync_httpx_client: httpx.Client,
) -> None:
    snapshot_sync_httpx_client.get(
        "https://jsonplaceholder.typicode.com/todos/1",
        headers={"X-Secret-Key": "secret"},
    )
