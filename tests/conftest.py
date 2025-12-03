import pytest


from http_snapshot._fixtures import *  # noqa: F403


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
