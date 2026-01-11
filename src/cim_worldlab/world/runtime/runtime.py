"""
runtime.py
==========
这一文件定义：WorldRuntime（世界运行时）——世界会动的心脏

在第 7 步，我们只有：
- t: 世界时间
- tick(): 产生事件，写入内存 EventLog

在第 8 步，我们加入“工程留痕”能力：
- 可选的 event_store（FileEventStore）
- tick 时除了写内存，也可以落盘写文件

为什么是“可选”？
- 你要能在单元测试、课堂演示时快速跑起来（不依赖磁盘）
- 但在真实工程里，留痕是必须的
- 所以我们用可选依赖：store 传了就写，不传就只记内存
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from cim_worldlab.world.events.event import Event
from cim_worldlab.world.runtime.event_log import EventLog
from cim_worldlab.world.persistence.file_event_store import FileEventStore


@dataclass
class WorldRuntime:
    """
    字段解释：
    - t: 世界时间（tick 计数）
    - event_log: 内存事件日志（用于“当前运行”的快速查看）
    - event_store: 可选的持久化事件存储（用于“跨进程/跨天”的留痕）
    """
    t: int = 0
    event_log: EventLog = field(default_factory=EventLog)
    event_store: Optional[FileEventStore] = None

    def tick(self, payload: Optional[Dict[str, Any]] = None) -> Event:
        """
        推进世界一步，产生一个事件，并进行留痕：

        1) t += 1
        2) 构造 Event
        3) 写入内存 event_log
        4) 如果配置了 event_store：追加写入文件（真正留痕）
        5) 返回事件
        """
        self.t += 1

        e = Event(
            t=self.t,
            type="WORLD_TICK",
            payload=payload or {},
        )

        # 内存留痕：快速、方便调试
        self.event_log.append(e)

        # 文件留痕：工程文明的核心（可追溯/可回放）
        if self.event_store is not None:
            self.event_store.append(e)

        return e

    @classmethod
    def replay_from_store(cls, store: FileEventStore) -> "WorldRuntime":
        """
        从事件存储中“回放 replay”，重建一个 WorldRuntime。

        思想非常重要：
        - 世界状态不是“凭空来的”
        - 世界状态来自历史事件的累积
        - 事件 = 事实；回放 = 复盘；重建 = 可信

        我们的 MVP 规则：
        - 读出所有事件 events
        - t 设置为最后一个事件的 t（没有事件则 t=0）
        - event_log 里也放入这些事件（方便调试与教学查看）
        - event_store 指向同一个 store（继续追加留痕）

        注意：更复杂的世界会有“状态机”，回放时会逐事件驱动状态变化；
        但目前我们只有 t，所以直接取最后 t 就够了。
        """
        events = store.load_all()
        rt = cls(t=0, event_store=store)

        # 回放：把历史事件重新放入内存日志
        for e in events:
            rt.event_log.append(e)
            rt.t = e.t  # 当前时间跟随历史事件推进（最后会停在最新）

        return rt
