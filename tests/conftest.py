import pytest


from http_snapshot._pytest_plugin import *  # noqa: F403


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
