"""
commands.py
===========
CLI 命令的“业务实现层”（可测试）

工程原则：
- argparse 只负责解析参数（薄）
- 命令的核心逻辑写成函数（厚、可测试）
- 这样你以后换成 Typer/Click 也不会改业务逻辑

我们提供 5 个命令能力：
1) serve: 启动 HTTP 输入服务（FastAPI/Uvicorn）
2) run_once: 世界跑一步（tick + ingest + metrics），并保存 cursor
3) run: 连续跑 N 次 run_once（带 sleep）
4) replay: 从 events.jsonl 回放重建状态（可选快照加速）
5) metrics: 基于 replay 打印指标（稳定、可重复）
"""

from __future__ import annotations

import os
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional

from cim_worldlab.cli.config import CliPaths, default_paths
from cim_worldlab.cli.utils import load_int, save_int
from cim_worldlab.world.gateway import FileQueueGateway
from cim_worldlab.world.persistence import FileEventStore, SnapshotStore
from cim_worldlab.world.persistence.file_input_queue import FileInputQueue
from cim_worldlab.world.runtime import WorldRuntime


def cmd_serve(host: str = "127.0.0.1", port: int = 8000, queue_path: Optional[Path] = None) -> None:
    """
    启动 HTTP 输入服务（阻塞运行）。

    说明：
    - HTTP 服务只负责接收 POST /v1/inputs 并写入 input_queue.jsonl
    - 它不跑世界、不做业务决策（边界清晰）
    """
    from cim_worldlab.http_server import main as server_main

    # 通过环境变量告诉 http_ingest_app 写到哪里
    paths = default_paths()
    qp = queue_path or paths.input_queue
    os.environ["CIM_INPUT_QUEUE_PATH"] = str(qp)

    os.environ["CIM_HTTP_HOST"] = host
    os.environ["CIM_HTTP_PORT"] = str(port)

    server_main()


def build_runtime_for_cli(paths: CliPaths) -> WorldRuntime:
    """
    构造一个 CLI 使用的 WorldRuntime：

    - gateway: FileQueueGateway（从 input_queue.jsonl 增量拉取外部输入）
    - event_store: FileEventStore（把世界事件写入 events.jsonl）
    - cursor: 从 out/cursor.txt 恢复（增量消费）

    注意：
    - runtime 的 state 会在 tick/ingest/_record 中自动更新（Step 10）
    """
    paths.base_dir.mkdir(parents=True, exist_ok=True)

    queue = FileInputQueue(path=paths.input_queue)
    cursor = load_int(paths.cursor, default=0)
    gateway = FileQueueGateway(queue=queue, cursor=cursor)

    store = FileEventStore(path=paths.events)

    return WorldRuntime(gateway=gateway, event_store=store)


def cmd_run_once(paths: Optional[CliPaths] = None, snapshot_every: int = 0) -> Dict[str, Any]:
    """
    世界跑一步（教学演示最常用）：

    1) tick 一次（推进世界时间）
    2) ingest_inputs（把外部输入转成 EXTERNAL_INPUT 事件）
    3) 打印/返回 metrics
    4) 保存 cursor（确保下次只消费新增输入）
    5) 可选：达到阈值时保存快照（Step 12）

    返回一个 dict，方便测试或未来接 UI。
    """
    p = paths or default_paths()
    rt = build_runtime_for_cli(p)

    tick_event = rt.tick({"cli": "run-once"})
    input_events = rt.ingest_inputs()
    m = rt.metrics()

    # 保存增量消费游标
    assert rt.gateway is not None  # build_runtime_for_cli 保证有 gateway
    save_int(p.cursor, rt.gateway.cursor)

    # 可选快照：每 N 条事件保存一次
    snapshot_saved = False
    if snapshot_every and snapshot_every > 0:
        snap = SnapshotStore(path=p.snapshot)
        snapshot_saved = rt.maybe_snapshot(snap, every_n_events=snapshot_every)

    return {
        "tick": tick_event.to_dict(),
        "ingested": [e.to_dict() for e in input_events],
        "metrics": asdict(m),
        "cursor": rt.gateway.cursor,
        "snapshot_saved": snapshot_saved,
        "paths": {
            "input_queue": str(p.input_queue),
            "events": str(p.events),
            "snapshot": str(p.snapshot),
            "cursor": str(p.cursor),
        },
    }


def cmd_run(ticks: int = 10, sleep_s: float = 0.2, paths: Optional[CliPaths] = None, snapshot_every: int = 0) -> None:
    """
    连续运行世界 N 次。

    用途：
    - 课堂演示“世界在持续运行”
    - 或者你未来做一个“后台 runner”

    sleep_s：
    - 每次循环之间 sleep 一下，避免 CPU 100%
    """
    for i in range(ticks):
        out = cmd_run_once(paths=paths, snapshot_every=snapshot_every)
        print(f"[run {i+1}/{ticks}] t={out['metrics']['t']} inputs={out['metrics']['input_count']} cursor={out['cursor']}")
        if sleep_s > 0:
            time.sleep(sleep_s)


def cmd_replay(paths: Optional[CliPaths] = None, fast: bool = True) -> Dict[str, Any]:
    """
    从 events.jsonl 回放重建世界（用于复盘/追责/教学）。

    fast=True：
    - 有 snapshot 时使用 replay_fast_from_store（快）
    - 没 snapshot 自动退化为全量 replay（稳）

    返回：
    - state / metrics / event_count
    """
    p = paths or default_paths()

    store = FileEventStore(path=p.events)
    snap = SnapshotStore(path=p.snapshot)

    if fast:
        rt = WorldRuntime.replay_fast_from_store(store, snap)
    else:
        rt = WorldRuntime.replay_from_store(store)

    m = rt.metrics()
    return {
        "t": rt.t,
        "state": {
            "t": rt.state.t,
            "tick_count": rt.state.tick_count,
            "input_count": rt.state.input_count,
            "last_input": rt.state.last_input,
        },
        "metrics": asdict(m),
        "event_count": len(rt.event_log),
        "paths": {
            "events": str(p.events),
            "snapshot": str(p.snapshot),
        },
    }


def cmd_metrics(paths: Optional[CliPaths] = None) -> Dict[str, Any]:
    """
    打印当前指标（从事件回放得到，结果稳定可重复）。
    """
    return cmd_replay(paths=paths, fast=True)["metrics"]
