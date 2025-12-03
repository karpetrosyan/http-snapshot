from http_snapshot._utils import suppress_errors
import pytest


from http_snapshot._pytest_plugin import *  # noqa: F403
from http_snapshot._pytest_plugin import pytest_addoption

# TODO: understand why pytest_addoption is called multiple times by pytest
pytest_addoption = suppress_errors(RuntimeError)(pytest_addoption)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
