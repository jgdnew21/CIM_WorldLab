"""
demo_13_run_world_once.py
=========================
Step 13 Demo - World Side（世界侧）

这个脚本做一件非常教学友好的事：
- 不启动 HTTP server（server 在另一个终端窗口）
- 只负责“跑世界一次”
  1) tick() 推进世界一步
  2) 从 FileQueueGateway 拉取新输入（只读新增部分）
  3) ingest_inputs() 写入事件留痕并更新状态
  4) 打印 ingest 到的事件与 metrics（让你“看见世界在发生什么”）

关键工程点：cursor（游标）
- FileQueueGateway 内部有 cursor，但脚本每次运行都会新建 gateway，cursor 会丢
- 为了演示“增量消费”，我们把 cursor 存到 out/demo_cursor.txt
- 下次运行脚本时，会从 cursor.txt 读上次位置，继续读新行（不会重复消费）
"""

from __future__ import annotations

from pathlib import Path

from cim_worldlab.world.gateway import FileQueueGateway
from cim_worldlab.world.persistence.file_input_queue import FileInputQueue
from cim_worldlab.world.runtime import WorldRuntime


QUEUE_PATH = Path("out/demo_input_queue.jsonl")
CURSOR_PATH = Path("out/demo_cursor.txt")


def load_cursor() -> int:
    """读取上一次消费到的行号（cursor）。如果没有就从 0 开始。"""
    if not CURSOR_PATH.exists():
        return 0
    raw = CURSOR_PATH.read_text(encoding="utf-8").strip()
    return int(raw) if raw else 0


def save_cursor(cursor: int) -> None:
    """把本次消费结束后的 cursor 保存下来，供下次运行继续消费。"""
    CURSOR_PATH.parent.mkdir(parents=True, exist_ok=True)
    CURSOR_PATH.write_text(str(cursor), encoding="utf-8")


def main() -> None:
    # 1) 构造队列 + 网关
    queue = FileInputQueue(path=QUEUE_PATH)

    # 2) 读取历史 cursor（保证多次运行只消费新增输入）
    cursor = load_cursor()
    gateway = FileQueueGateway(queue=queue, cursor=cursor)

    # 3) 世界运行一次：tick + ingest
    rt = WorldRuntime(gateway=gateway)

    tick_event = rt.tick({"demo": "step13"})
    print("TICK:", tick_event.to_dict())

    events = rt.ingest_inputs()
    print(f"INGESTED_INPUT_EVENTS: {len(events)}")
    for e in events:
        print("  INPUT_EVENT:", e.to_dict())

    # 4) 打印指标（可观测性）
    m = rt.metrics()
    print("METRICS:", m)

    # 5) 保存 cursor（关键：下次只读新行）
    save_cursor(gateway.cursor)
    print("CURSOR_SAVED:", gateway.cursor)
    print("QUEUE_FILE:", QUEUE_PATH.resolve())


if __name__ == "__main__":
    main()
