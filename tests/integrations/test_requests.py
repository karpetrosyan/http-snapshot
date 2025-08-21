from typing import Any
import inline_snapshot
import requests
import pytest


@pytest.mark.parametrize(
    "http_snapshot",
    [inline_snapshot.external("uuid:4b3f8eb7-5c88-4cbc-86e7-61f23e35846e.json")],
)
def test_basic_snapshot(
    snapshot_requests_session: requests.Session, http_snapshot: Any
) -> None:
    response = snapshot_requests_session.get("https://hishel.com")
    assert response.status_code == 200
