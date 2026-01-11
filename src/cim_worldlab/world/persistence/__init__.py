"""
persistence 包：负责“把世界历史写下来”。

- FileEventStore：事件写入 JSONL（append-only）
- SnapshotStore：状态快照 JSON（回放加速）
"""
from .file_event_store import FileEventStore
from .snapshot_store import SnapshotStore

__all__ = ["FileEventStore", "SnapshotStore"]
