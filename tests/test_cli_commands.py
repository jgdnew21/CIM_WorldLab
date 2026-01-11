"""
test_cli_commands.py
====================
只测试 CLI 的“业务实现层”（commands.py），不测试 argparse，也不启动 HTTP server。

这符合工程测试原则：
- 单元测试应快速、稳定、无外部依赖
"""

from pathlib import Path

from cim_worldlab.cli.config import CliPaths
from cim_worldlab.cli.commands import cmd_run_once, cmd_replay
from cim_worldlab.world.persistence.file_input_queue import FileInputQueue
from cim_worldlab.world.events.external_input import ExternalInput


def test_cmd_run_once_writes_events_and_saves_cursor(tmp_path: Path):
    out_dir = tmp_path / "out"
    paths = CliPaths(base_dir=out_dir)

    # 预写入一个输入到 input_queue
    q = FileInputQueue(path=paths.input_queue)
    q.append(ExternalInput(source="plugin", channel="equipment", name="TEMP", data={"v": 1}, trace_id="X"))

    out = cmd_run_once(paths=paths, snapshot_every=0)

    # 至少有 1 个 tick 事件
    assert out["tick"]["type"] == "WORLD_TICK"
    # ingest 到 1 条输入事件
    assert len(out["ingested"]) == 1
    assert out["ingested"][0]["type"] == "EXTERNAL_INPUT"
    # cursor 文件应该存在
    assert paths.cursor.exists()
    # events 文件应该存在
    assert paths.events.exists()


def test_cmd_replay_returns_state_and_metrics(tmp_path: Path):
    out_dir = tmp_path / "out"
    paths = CliPaths(base_dir=out_dir)

    # 先跑一次，产生事件
    cmd_run_once(paths=paths, snapshot_every=0)

    rep = cmd_replay(paths=paths, fast=True)
    assert rep["event_count"] >= 1
    assert "metrics" in rep
    assert "state" in rep
