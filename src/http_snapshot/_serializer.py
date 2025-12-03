from __future__ import annotations

import json
from typing import Any, Iterable, Mapping, Optional
import inline_snapshot
import pytest
import base64

from ._models import Headers, Request, Response


class SnapshotSerializerOptions:
    def __init__(
        self,
        include_request: bool = False,
        exclude_request_headers: Iterable[str] = (),
        exclude_response_headers: Iterable[str] = (),
    ) -> None:
        self.include_request = include_request
        self.exclude_request_headers = set(
            header.lower() for header in exclude_request_headers
        )
        self.exclude_response_headers = set(
            header.lower() for header in exclude_response_headers
        )


def encode_content(content: bytes, content_type: str) -> str | dict[str, Any]:
    if "application/json" in content_type:
        return json.loads(content)  # type: ignore[no-any-return]
    elif content_type.startswith("text/"):
        return content.decode("utf-8")
    else:
        # base64 any other binary content
        return base64.b64encode(content).decode("utf-8")


def decode_content(encoded_content: str | dict[str, Any], content_type: str) -> bytes:
    if "application/json" in content_type:
        return json.dumps(encoded_content).encode("utf-8")
    elif content_type.startswith("text/"):
        assert isinstance(encoded_content, str), (
            "Expected encoded content to be a string for text content"
        )
        return encoded_content.encode("utf-8")
    else:
        assert isinstance(encoded_content, str), (
            "Expected encoded content to be a string for binary content"
        )
        # decode base64 for other binary content
        return base64.b64decode(encoded_content)


def exclude_sensitive_request_headers(
    headers: Mapping[str, str], options: Optional[SnapshotSerializerOptions] = None
) -> dict[str, str]:
    options = options or SnapshotSerializerOptions()
    return {
        k: v
        for k, v in headers.items()
        if k.lower() not in options.exclude_request_headers
        and k.lower() not in ("authorization", "cookie")
    }


def exclude_sensitive_response_headers(
    headers: Mapping[str, str],
    options: Optional[SnapshotSerializerOptions] = None,
) -> dict[str, str]:
    options = options or SnapshotSerializerOptions()
    return {
        k: v
        for k, v in headers.items()
        if k.lower() not in options.exclude_response_headers
        and k.lower()
        not in (
            "set-cookie",
            "www-authenticate",
            "proxy-authenticate",
            "authentication-info",
            "proxy-authentication-info",
            "transfer-encoding",
            "content-encoding",
        )
    }


def internal_to_snapshot(
    pairs: list[tuple[Request, Response]],
    options: Optional[SnapshotSerializerOptions] = None,
) -> list[dict[str, Any]]:
    options = options or SnapshotSerializerOptions()
    to_compare = []

    for request, response in pairs:
        repr: dict[str, Any] = {}

        if options.include_request:
            repr["request"] = {
                "method": request.method,
                "url": str(request.url),
                "headers": exclude_sensitive_request_headers(
                    dict(request.headers), options
                ),
                "body": encode_content(
                    request.body, request.headers.get("Content-Type", "")
                ),
            }

        repr["response"] = {
            "status_code": response.status_code,
            "headers": exclude_sensitive_response_headers(
                dict(response.headers), options
            ),
            "body": encode_content(
                response.body, response.headers.get("Content-Type", "")
            ),
        }

        to_compare.append(repr)
    return to_compare


def snapshot_to_internal(
    snapshot: inline_snapshot.Snapshot[list[dict[str, Any]]],
) -> list[Response]:
    responses = []

    value = inline_snapshot.get_snapshot_value(snapshot)

    if value is None:
        raise RuntimeError(
            "Snapshot value was not found. Create it first using the inline snapshot create option."
        )

    for item in value:
        headers = Headers(item["response"]["headers"])
        response = Response(
            status_code=item["response"]["status_code"],
            headers=headers,
            body=decode_content(
                item["response"]["body"],
                headers.get("Content-Type", ""),
            ),
        )
        responses.append(response)

    return responses


@pytest.fixture
def snapshot() -> Any:
    return inline_snapshot.external("uuid:93ec4e8a-8760-4cd1-8330-df818d448e0d.json")
