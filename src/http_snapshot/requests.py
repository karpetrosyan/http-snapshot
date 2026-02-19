try:
    import requests
except ImportError:
    raise ImportError(
        "requests is not installed. Please install http-snapshot with requests feature [pip install http-snapshot[requests]]"
    )


from typing import Any, Optional
import inline_snapshot

from ._serializer import SnapshotSerializerOptions, internal_to_snapshot

__all__ = ["RequestsSnapshotSession"]


class RequestsSnapshotSession:
    def __init__(
        self,
        snapshot: inline_snapshot.Snapshot[list[dict[str, Any]]],
        is_recording: bool,
        serializer_options: Optional[SnapshotSerializerOptions] = None,
    ):
        self.snapshot = snapshot
        self.is_recording = is_recording
        self.serializer_options = serializer_options or SnapshotSerializerOptions()
        self._session: Optional[requests.Session] = None
        self._adapter: Optional[Any] = None

    def __enter__(self) -> requests.Session:
        from ._integrations._requests import SnapshotAdapter

        self._session = requests.Session()
        self._adapter = SnapshotAdapter(
            snapshot=self.snapshot, is_recording=self.is_recording
        )
        self._session.mount("http://", self._adapter)
        self._session.mount("https://", self._adapter)

        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self._adapter and self._adapter.is_recording:
                assert (
                    internal_to_snapshot(
                        self._adapter.collected_pairs,
                        self.serializer_options,
                    )
                    == self._adapter.snapshot
                )
        finally:
            if self._session:
                self._session.close()
