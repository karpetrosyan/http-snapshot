# http-snapshot

`http-snapshot` is a pytest plugin that captures and snapshots HTTP requests/responses made with popular Python HTTP clients like `httpx` and `requests`. It uses [inline-snapshot](https://github.com/15r10nk/inline-snapshot) to store HTTP interactions as JSON files, enabling fast and reliable HTTP testing without making actual network calls.

## Features

- 🚀 **Support for multiple HTTP clients**: `httpx` (async) and `requests` (sync)
- 📸 **Automatic HTTP interaction capture**: Records both requests and responses
- 🔒 **Security-aware**: Automatically excludes sensitive headers like authorization and cookies
- ⚙️ **Configurable**: Control what gets captured and what gets excluded
- 🧪 **pytest integration**: Works seamlessly with your existing pytest test suite
- 📁 **External snapshots**: Stores snapshots in organized JSON files

## Installation

```bash
pip install http-snapshot
```

For specific HTTP client support:

```bash
# For httpx support
pip install http-snapshot[httpx]

# For requests support
pip install http-snapshot[requests]

# For both
pip install http-snapshot[httpx,requests]
```

## Quick Start

### Using with httpx (async)

```python
import httpx
import pytest
import inline_snapshot

@pytest.mark.anyio
@pytest.mark.parametrize(
    "http_snapshot",
    [inline_snapshot.external("uuid:my-test-snapshot.json")],
)
async def test_api_call(snapshot_httpx_client: httpx.AsyncClient) -> None:
    # This will be captured on first run, replayed on subsequent runs
    response = await snapshot_httpx_client.get("https://api.example.com/users")
    assert response.status_code == 200
    assert "users" in response.json()
```

### Using with requests (sync)

```python
import requests
import pytest
import inline_snapshot

@pytest.mark.parametrize(
    "http_snapshot",
    [inline_snapshot.external("uuid:my-test-snapshot.json")],
)
def test_api_call(snapshot_requests_session: requests.Session) -> None:
    # This will be captured on first run, replayed on subsequent runs
    response = snapshot_requests_session.get("https://api.example.com/users")
    assert response.status_code == 200
    assert "users" in response.json()
```

## How It Works

### Live Mode vs Replay Mode

The plugin operates in two modes:

1. **Live Mode**: When `HTTP_SNAPSHOT_LIVE=1` is set, actual HTTP requests are made and responses are captured
2. **Replay Mode**: When not in live mode, previously captured responses are replayed

### Running in Live Mode

```bash
# Capture new snapshots
HTTP_SNAPSHOT_LIVE=1 pytest tests/

# Replay existing snapshots (default)
pytest tests/
```

## Configuration Options

You can customize what gets captured using `SnapshotSerializerOptions`:

```python
import pytest
import inline_snapshot
from http_snapshot._serializer import SnapshotSerializerOptions

@pytest.mark.parametrize(
    "http_snapshot, http_snapshot_serializer_options",
    [
        (
            inline_snapshot.external("uuid:my-test-snapshot.json"),
            SnapshotSerializerOptions(
                exclude_request_headers=["X-API-Key"],
                include_request=True,  # Include request details in snapshot
            ),
        ),
    ],
)
def test_with_custom_options(
    snapshot_requests_session: requests.Session,
    http_snapshot_serializer_options: SnapshotSerializerOptions,
) -> None:
    response = snapshot_requests_session.get(
        "https://api.example.com/protected",
        headers={"X-API-Key": "secret-key"}
    )
    assert response.status_code == 200
```

### Available Options

- `include_request`: Whether to include request details in snapshots (default: `True`)
- `exclude_request_headers`: List of request headers to exclude from snapshots
- `exclude_response_headers`: List of response headers to exclude from snapshots

By default, the following sensitive headers are always excluded:

- **Request**: `authorization`, `cookie`
- **Response**: `set-cookie`, `www-authenticate`, `proxy-authenticate`, `authentication-info`, `proxy-authentication-info`, `transfer-encoding`, `content-encoding`

## Snapshot Format

Snapshots are stored as JSON files with the following structure:

```json
[
  {
    "request": {
      "method": "GET",
      "url": "https://api.example.com/users",
      "headers": {
        "host": "api.example.com",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "connection": "keep-alive",
        "user-agent": "python-httpx/0.28.1"
      },
      "body": ""
    },
    "response": {
      "status_code": 200,
      "headers": {
        "date": "Thu, 21 Aug 2025 15:49:45 GMT",
        "content-type": "application/json; charset=utf-8",
        "connection": "keep-alive",
        "server": "nginx/1.18.0"
      },
      "body": "{\n  \"users\": [\n    {\n      \"id\": 1,\n      \"name\": \"John Doe\",\n      \"email\": \"john@example.com\"\n    }\n  ]\n}"
    }
  }
]
```

### Content Encoding

The plugin intelligently handles different content types:

- **JSON**: Formatted with proper indentation for readability
- **Text**: Stored as UTF-8 strings
- **Binary**: Base64 encoded

## Advanced Examples

### Testing API with Multiple Requests

```python
@pytest.mark.anyio
@pytest.mark.parametrize(
    "http_snapshot",
    [inline_snapshot.external("uuid:multi-request-test.json")],
)
async def test_multiple_requests(snapshot_httpx_client: httpx.AsyncClient) -> None:
    # Create a user
    create_response = await snapshot_httpx_client.post(
        "https://api.example.com/users",
        json={"name": "Alice", "email": "alice@example.com"}
    )
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    # Fetch the user
    get_response = await snapshot_httpx_client.get(
        f"https://api.example.com/users/{user_id}"
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Alice"
```

### Testing with Authentication

```python
@pytest.mark.parametrize(
    "http_snapshot, http_snapshot_serializer_options",
    [
        (
            inline_snapshot.external("uuid:auth-test.json"),
            SnapshotSerializerOptions(exclude_request_headers=["Authorization"]),
        ),
    ],
)
def test_authenticated_request(
    snapshot_requests_session: requests.Session,
    http_snapshot_serializer_options,
) -> None:
    # The Authorization header will be excluded from the snapshot
    response = snapshot_requests_session.get(
        "https://api.example.com/profile",
        headers={"Authorization": "Bearer secret-token"}
    )
    assert response.status_code == 200
```

## Best Practices

1. **Exclude sensitive data**: Always exclude headers containing secrets, tokens, or personal data
2. **Review snapshots**: Check generated snapshot files into version control and review changes
3. **Use live mode sparingly**: Only run in live mode when you need to update snapshots
