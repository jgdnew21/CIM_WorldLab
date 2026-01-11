"""
engine.py
=========
Step 17：最小策略引擎（Policy Engine v0）

核心思想：
- Policy Engine 本质上是一个“判断器”：
  输入：一个事件（通常是 EXTERNAL_INPUT）
  输出：0 个或多个 PolicyDecision

重要工程原则：
- 先把它写成纯函数 evaluate_event(...)
- 不要在这里写文件、写网络、改全局状态
- 这样你可以：
  1) 很容易写单元测试
  2) 很容易 replay（同样输入得到同样决策）
  3) 未来扩展规则也很自然

MVP 只做一条规则：
- 如果设备温度 temp_c > threshold
  -> recommended_action = "PAUSE"
  -> severity = "ALERT"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from cim_worldlab.world.events.event import Event
from cim_worldlab.world.events.external_input import EXTERNAL_INPUT_TYPE
from cim_worldlab.world.events.policy_decision import PolicyDecision


@dataclass(frozen=True)
class PolicyConfig:
    """
    策略引擎配置（阈值等可调参数）。
    以后你会在不同 factory/不同机台上使用不同 config。
    """
    temp_high_threshold_c: float = 92.0  # 教学默认：92℃ 以上就算偏危险


def _extract_temp_c(payload: Dict[str, Any]) -> Optional[float]:
    """
    从 EXTERNAL_INPUT.payload 中提取 temp_c。

    设计说明：
    - payload 结构来自 ExternalInput.to_event()
      payload = {source, channel, name, data, trace_id?}
    - temp_c 在 payload["data"]["temp_c"]

    返回：
    - float：提取到
    - None：不存在或不可转换
    """
    data = payload.get("data", {})
    if not isinstance(data, dict):
        return None

    v = data.get("temp_c", None)
    if v is None:
        return None

    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def evaluate_event(e: Event, config: PolicyConfig = PolicyConfig()) -> List[PolicyDecision]:
    """
    输入一个事件 e，输出 0..N 个决策（PolicyDecision）。

    目前只对 EXTERNAL_INPUT 感兴趣，其它事件返回空。
    """
    if e.type != EXTERNAL_INPUT_TYPE:
        return []

    channel = e.payload.get("channel")
    name = e.payload.get("name")

    # 只关心设备温度输入
    if channel != "equipment" or name != "TEMP_READING":
        return []

    temp_c = _extract_temp_c(e.payload)
    if temp_c is None:
        return []

    threshold = config.temp_high_threshold_c

    # 命中规则：温度超过阈值
    if temp_c > threshold:
        trace_id = e.payload.get("trace_id")  # 输入若有 trace_id，我们也带上，方便串联
        reason = f"TEMP too high: temp_c={temp_c} > threshold={threshold}. Recommend PAUSE."

        d = PolicyDecision(
            rule_id="TEMP_HIGH_PAUSE",
            severity="ALERT",
            recommended_action="PAUSE",
            reason=reason,
            evidence={"temp_c": temp_c, "threshold_c": threshold},
        )
        # 注意：这里不生成 Event（保持纯），Event 由 runtime 负责写入事件流
        return [d]

    return []
