"""
file_queue_gateway.py
=====================
FileQueueGateway：基于文件队列的插件网关实现

在 Step 9 我们定义了 PluginGateway 接口：
- pull_inputs() -> List[ExternalInput]

现在我们提供一个“真实实现”：
- 输入来自 FileInputQueue（JSONL）
- 网关内部保存 cursor，pull 时只读取新行
"""

from __future__ import annotations

from dataclasses import dataclass

from cim_worldlab.world.events.external_input import ExternalInput
from cim_worldlab.world.gateway.plugin_gateway import PluginGateway
from cim_worldlab.world.persistence.file_input_queue import FileInputQueue


@dataclass
class FileQueueGateway(PluginGateway):
    """
    queue：文件输入队列
    cursor：已消费到第几行（0 表示没消费）
    """
    queue: FileInputQueue
    cursor: int = 0

    def pull_inputs(self) -> list[ExternalInput]:
        """
        拉取新输入：
        - 从 queue.read_since(cursor) 读取新输入
        - 更新 cursor
        - 返回新输入列表
        """
        items, new_cursor = self.queue.read_since(self.cursor)
        self.cursor = new_cursor
        return items
