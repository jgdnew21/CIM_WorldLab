"""
main.py
=======
CLI 入口（argparse）

我们选择标准库 argparse（不引入额外依赖）：
- 对初学者更友好
- 更容易理解“命令行解析本质”
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cim_worldlab.cli.commands import cmd_serve, cmd_run_once, cmd_run, cmd_replay


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cim_worldlab", description="CIM_WorldLab CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    # serve
    ps = sub.add_parser("serve", help="Start HTTP input server (FastAPI)")
    ps.add_argument("--host", default="127.0.0.1", help="Host to bind")
    ps.add_argument("--port", type=int, default=8000, help="Port to bind")
    ps.add_argument("--queue", type=Path, default=None, help="Queue file path (jsonl)")

    # run-once
    pr = sub.add_parser("run-once", help="Run one tick + ingest inputs, print metrics")
    pr.add_argument("--snapshot-every", type=int, default=0, help="Save snapshot every N events (0=disable)")
    pr.add_argument("--pretty",action="store_true",help="Pretty output for projector")


    # run
    prun = sub.add_parser("run", help="Run N ticks, repeatedly calling run-once")
    prun.add_argument("--ticks", type=int, default=10)
    prun.add_argument("--sleep", type=float, default=0.2)
    prun.add_argument("--snapshot-every", type=int, default=0, help="Save snapshot every N events (0=disable)")

    # replay
    prep = sub.add_parser("replay", help="Replay world from events store and print state/metrics")
    prep.add_argument("--full", action="store_true", help="Force full replay (ignore snapshot)")

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "serve":
        cmd_serve(host=args.host, port=args.port, queue_path=args.queue)
        return 0

    if args.cmd == "run-once":
        out = cmd_run_once(snapshot_every=args.snapshot_every)

        if args.pretty:
            # ========= 投屏友好输出 =========
            # 设计原则：
            # - 一行一个重点指标：t / tick / inputs / cursor
            # - 再补充“最近发生了什么”：last_input / last_action
            # - 避免打印长 JSON（投影屏幕上看不清）

            m = out["metrics"]
            
            # 1) 总览行：世界时间、tick 次数、输入总数、cursor（指向事件日志的位置）
            print(
                f"t={m['t']}  "
                f"ticks={m['tick_count']}  "
                f"inputs={m['input_count']}  "
                f"cursor={out['cursor']}"
            )

            # 2) 最近输入（last_input_summary）
            #    - 这是“事实层”：外部输入是什么？来自哪里？属于哪个通道？
            if m.get("last_input_summary"):
                li = m["last_input_summary"]
                print(
                    "last_input:"
                    f" source={li.get('source')}"
                    f" channel={li.get('channel')}"
                    f" name={li.get('name')}"
                )
            # 3) 输入通道分布（inputs_by_channel）
            #    - 方便快速看出：设备通道、订单通道、人为通道各来了多少输入
            print(f"inputs_by_channel: {m.get('inputs_by_channel', {})}")
            
            # 4) ===== Step18：动作留痕（ACTION_EXECUTED） =====
            #    - POLICY_DECISION 只是“建议/判断”
            #    - ACTION_EXECUTED 才是“真的执行了什么”的留痕
            #
            # 这里我们不直接打印 state，而是打印 metrics 里的摘要：
            # - action_count：累计执行动作次数
            # - last_action_summary：最近一次动作的投屏摘要（action_type + reason）

            # 4.1 动作累计次数（如果旧数据没有这个字段，默认 0）
            print(f"action_count: {m.get('action_count', 0)}")

            # 4.2 最近动作摘要（如果还没有动作，就打印 none）
            last_action = m.get("last_action_summary")
            if not last_action:
                print("last_action: (none)")
            else:
                # action_type：动作类型，例如 SLOW_DOWN / STOP / OBSERVE / NOOP
                action_type = last_action.get("action_type", "")
                # reason：执行理由（投屏最重要的一句话）
                reason = last_action.get("reason", "")
                print(f"last_action: {action_type}  because {reason}")
        else:
            print(json.dumps(out, ensure_ascii=False, indent=2))

        return 0


    if args.cmd == "run":
        cmd_run(ticks=args.ticks, sleep_s=args.sleep, snapshot_every=args.snapshot_every)
        return 0

    if args.cmd == "replay":
        out = cmd_replay(fast=not args.full)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    raise SystemExit("Unknown command")
