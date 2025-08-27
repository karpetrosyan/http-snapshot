import inline_snapshot
import requests
import pytest

from http_snapshot._serializer import SnapshotSerializerOptions


@pytest.mark.parametrize(
    "http_snapshot",
    [inline_snapshot.external("uuid:4b3f8eb7-5c88-4cbc-86e7-61f23e35846e.json")],
)
def test_basic_snapshot(snapshot_requests_session: requests.Session) -> None:
    response = snapshot_requests_session.get("https://hishel.com")
    assert response.status_code == 200


@pytest.mark.parametrize(
    "http_snapshot, http_snapshot_serializer_options",
    [
        (
            inline_snapshot.external("uuid:7e83e278-a6a7-4f12-9a4b-bca4103347e7.json"),
            SnapshotSerializerOptions(
                exclude_request_headers=["X-Secret-Key"],
            ),
        )
    ],
)
def test_with_excluded_headers(snapshot_requests_session: requests.Session) -> None:
    response = snapshot_requests_session.get(
        "https://hishel.com",
        headers={"X-Secret-Key": "supersecret"},
    )

    assert response.status_code == 200
