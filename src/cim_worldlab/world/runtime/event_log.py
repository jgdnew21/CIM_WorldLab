# ----------------------------
# 2) 事件日志 EventLog（先做内存版）
# ----------------------------
"""
event_log.py
============
这一文件定义：EventLog（事件日志）

你可以把 EventLog 理解为：
- 一个“事件列表”
- 所有发生过的 Event 都会被 append 进去
- 这是最简单的 MVP（最小可用版本）

后续升级方向：
- persistence：把事件写入磁盘文件 / 数据库（真正留痕）
- replay：从事件日志重建世界状态（像“回放录像”）
"""

from dataclasses import dataclass, field
from typing import List, Optional

from cim_worldlab.world.events.event import Event


@dataclass
class EventLog:
    """
    EventLog 内部用一个 list 保存事件。

    这里用 dataclass 的好处：
    - 写起来简洁
    - 字段默认值用 default_factory，避免多个实例共享同一个 list（这是 Python 常见坑）

    _events：
    - 这里用下划线开头，表示“内部字段”
      （不是强制私有，但团队约定：外部不要直接改它）
    """
    _events: List[Event] = field(default_factory=list)

    def append(self, e: Event) -> None:
        """
        追加事件到日志中。

        参数 e: 一个 Event 对象
        返回值 None：表示“只做副作用（记录），不返回值”
        """
        self._events.append(e)

    def all(self) -> List[Event]:
        """
        返回所有事件。

        注意：这里直接返回内部 list 的引用（MVP 阶段够用）
        更严谨的版本可能会返回拷贝：return list(self._events)
        """
        return self._events

    def last(self) -> Optional[Event]:
        """
        返回最后一个事件；如果还没有事件，返回 None。

        Optional[Event] 的意思是：可能是 Event，也可能是 None
        """
        return self._events[-1] if self._events else None

    def __len__(self) -> int:
        """
        让 len(event_log) 可以工作。
        Python 会在调用 len(x) 时，尝试执行 x.__len__().
        """
        return len(self._events)