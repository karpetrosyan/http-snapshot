import pytest
from ._fixtures import *  # noqa: F403


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--http-record",
        action="store_true",
        default=False,
        help="Make real HTTP requests and record new snapshots when missing",
    )
