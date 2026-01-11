"""
test_persistence_replay.py
==========================
这一组测试验证“工程留痕”的闭环能力：

1) 运行时 tick 能把事件写入文件（JSONL）
2) 新进程（新 runtime）可以从文件回放 replay，重建世界时间 t
3) 回放后的 runtime 继续 tick，会在同一个文件上追加留痕（历史不断裂）
"""

from pathlib import Path

from cim_worldlab.world.persistence import FileEventStore
from cim_worldlab.world.runtime import WorldRuntime


def test_tick_persists_and_replay_rebuilds_time(tmp_path: Path):
    # tmp_path 是 pytest 提供的临时目录（每次测试都会是干净的）
    log_path = tmp_path / "events.jsonl"
    store = FileEventStore(path=log_path)

    # 1) 创建 runtime，并配置 event_store：tick 时会落盘
    rt1 = WorldRuntime(event_store=store)
    rt1.tick({"i": 1})
    rt1.tick({"i": 2})
    assert rt1.t == 2

    # 文件应该存在，并且至少有 2 行
    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2

    # 2) “新 runtime”从 store 回放 replay
    rt2 = WorldRuntime.replay_from_store(store)
    assert rt2.t == 2
    assert len(rt2.event_log) == 2  # 内存日志里也有历史事件

    # 3) 回放后继续 tick：会追加写第三行
    rt2.tick({"i": 3})
    assert rt2.t == 3
    lines2 = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines2) == 3
