# ----------------------------
# 1) 事件模型 Event（可序列化）
# ----------------------------
"""
event.py
========
这一文件定义：Event（事件）

你可以把“事件”理解为：
- 世界里发生了一件事（一个事实记录）
- 之后我们可以把事件写入日志、落盘、回放(replay)

为什么要“事件”？
- 工程系统最怕“说不清发生了什么”
- 事件就是“可追溯”的最小记录单位
- 这是 EAP / CIM / 工程文明里最核心的思想之一：**留痕**
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict


@dataclass(frozen=True)
class Event:
    """
    Event 是一个“不可变”的数据对象（frozen=True）
    - frozen=True：创建后字段不能再被修改
      这样做的好处：事件一旦发生，就不能“篡改历史”

    字段解释：
    - t: 世界时间（第几个 tick）
    - type: 事件类型（字符串），例如 "WORLD_TICK"
    - payload: 事件附带的数据（字典），要求是“可 JSON 化”的结构
      （也就是里面放 int/float/str/bool/list/dict 等）
    """
    t: int
    type: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """
        把 Event 转为 dict，方便 json.dumps(...) 序列化。

        dataclasses.asdict 会把 dataclass 递归转为 dict。
        例如：
        Event(t=1, type="WORLD_TICK", payload={"i": 0})
        -> {"t": 1, "type": "WORLD_TICK", "payload": {"i": 0}}
        """
        return asdict(self)