from typing import Any

import inline_snapshot
import pytest

from http_snapshot._serializer import SnapshotSerializerOptions
from http_snapshot.requests import RequestsSnapshotSession


@pytest.mark.parametrize(
    "http_snapshot",
    [inline_snapshot.external("uuid:4b3f8eb7-5c88-4cbc-86e7-61f23e35846e.json")],
)
def test_basic_snapshot(
    http_snapshot: inline_snapshot.Snapshot[Any],
    http_snapshot_serializer_options: SnapshotSerializerOptions,
    is_recording: bool,
) -> None:
    with RequestsSnapshotSession(
        snapshot=http_snapshot,
        is_recording=is_recording,
    ) as session:
        response = session.get("https://hishel.com")

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
def test_with_excluded_headers(
    http_snapshot: inline_snapshot.Snapshot[Any],
    http_snapshot_serializer_options: SnapshotSerializerOptions,
    is_recording: bool,
) -> None:
    with RequestsSnapshotSession(
        snapshot=http_snapshot,
        is_recording=is_recording,
    ) as session:
        response = session.get(
            "https://hishel.com",
            headers={"X-Secret-Key": "supersecret"},
        )

    assert response.status_code == 200
