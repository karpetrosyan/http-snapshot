from typing import cast

import pytest

from ._serializer import SnapshotSerializerOptions


__all__ = [
    "http_snapshot_serializer_options",
    "is_recording",
]


@pytest.fixture
def is_recording(request: pytest.FixtureRequest) -> bool:
    try:
        return cast(bool, request.config.getoption("--http-record"))
    except Exception:
        return False


@pytest.fixture
def http_snapshot_serializer_options() -> SnapshotSerializerOptions:
    return SnapshotSerializerOptions()
