"""
world_metrics.py
================
这一文件定义：WorldMetrics（世界指标快照）

为什么要“指标”？
- 事件告诉你“发生了什么”（事实）
- 状态告诉你“当前是什么样”（结果）
- 指标告诉你“我该关注什么”（管理与决策所需的视角）

在半导体 / EAP / CIM 体系里，指标的作用非常大：
- 让人能在复杂系统中快速判断：稳不稳？危险不危险？趋势如何？
- 指标也是后续触发告警（FDC/SPC/OMS）的基础

MVP 我们先做几条最直观的指标：
- t: 当前世界时间
- tick_count: tick 次数（来自 state）
- input_count: 外部输入累计数（来自 state）
- inputs_by_channel: 按 channel 统计输入数量（来自 event_log）
- last_input_summary: 最近输入的简要信息（channel/name/source）
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class WorldMetrics:
    """
    指标快照：不可变（frozen=True），每次计算产生一个新对象。
    """
    t: int
    tick_count: int
    input_count: int
    inputs_by_channel: Dict[str, int]
    last_input_summary: Optional[Dict[str, str]]
