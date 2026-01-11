"""
plugin_gateway.py
=================
这一文件定义：PluginGateway（插件网关接口）

你可以把 PluginGateway 理解为：
- “世界”和“外部插件”的边界（boundary）
- runtime 不关心外部是 HTTP、gRPC、消息队列还是本地函数
- runtime 只关心：我能不能拿到输入？我能不能把输出发出去？

MVP 阶段我们只做：pull_inputs()
- 世界每个 tick 都可以问网关：有没有新的外部输入？
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from cim_worldlab.world.events.external_input import ExternalInput


class PluginGateway(Protocol):
    """
    Protocol = “结构化的接口”：
    - 只要一个类实现了同名方法，就算符合这个接口（鸭子类型）
    - 好处：不强迫继承，测试替身也好写
    """

    def pull_inputs(self) -> List[ExternalInput]:
        """
        拉取外部输入队列。

        返回：
        - ExternalInput 的列表（可能为空）
        语义：
        - “把现在能拿到的输入都给我”
        """
        raise NotImplementedError


@dataclass
class FakePluginGateway:
    """
    FakePluginGateway：测试替身（test double）
    - 用内存 list 模拟“外部插件发来的输入”
    - pytest 里我们会用它来验证 runtime 的行为

    为什么要 Fake？
    - 真实 HTTP 很难在单元测试里稳定复现
    - 工程上：先把业务逻辑测牢，再接外部系统
    """
    queued: List[ExternalInput]

    def pull_inputs(self) -> List[ExternalInput]:
        """
        一次性把队列里的输入取走（并清空）。
        这模拟了“消费队列”的行为。
        """
        items = list(self.queued)
        self.queued.clear()
        return items
