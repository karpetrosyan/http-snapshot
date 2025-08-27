from typing import Any

import sys

if sys.version_info >= (3, 11):
    from typing import assert_never as assert_never
else:

    def assert_never(value: Any, message: str = "Unexpected value") -> Any:
        raise AssertionError(f"{message}: {value!r}") from None
