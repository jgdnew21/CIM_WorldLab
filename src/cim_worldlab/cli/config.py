"""
config.py
=========
CLI 配置集中管理（非常重要的工程习惯）

为什么要集中管理路径？
- 否则每个命令都在各处硬编码 out/xxx.jsonl
- 未来你想改目录结构（或支持不同项目路径）会很痛苦
- 集中管理能让 CLI 行为一致，也更利于测试

这里的默认路径只服务于“本地教学/演示”的 MVP：
- input_queue.jsonl：HTTP server 写入的输入队列
- events.jsonl：世界运行产生的事件留痕
- snapshot.json：快照（用于 replay 加速）
- cursor.txt：FileQueueGateway 的消费游标（增量消费输入队列）
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CliPaths:
    base_dir: Path

    @property
    def input_queue(self) -> Path:
        return self.base_dir / "input_queue.jsonl"

    @property
    def events(self) -> Path:
        return self.base_dir / "events.jsonl"

    @property
    def snapshot(self) -> Path:
        return self.base_dir / "snapshot.json"

    @property
    def cursor(self) -> Path:
        return self.base_dir / "cursor.txt"


def default_paths() -> CliPaths:
    """
    默认把运行产物放到 out/ 目录下。
    """
    return CliPaths(base_dir=Path("out"))
