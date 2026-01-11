"""
persistence 包：负责“把世界历史写下来”。

当前只有最小实现：
- FileEventStore：把事件写入 JSONL 文件，并可读出用于回放
"""
from .file_event_store import FileEventStore

__all__ = ["FileEventStore"]
