"""
policy_decision.py
==================
Step 17：策略决策事件（Policy Decision Event）

为什么要有 POLICY_DECISION？
- EXTERNAL_INPUT：事实（发生了什么输入）
- POLICY_DECISION：判断（基于事实做出的“建议动作/理由”）
- ACTION_EXECUTED：执行（真的做了什么动作）——Step 18 再做

把“判断”作为事件留痕的好处：
- 可解释：你可以清楚看到为什么系统建议暂停
- 可复盘：replay 时可以重现当时的判断
- 可扩展：未来你有很多 policy（FDC/SPC/OMS…），都能统一记录为 decision

本事件 payload 设计（MVP）：
- rule_id：哪个规则命中（例如 TEMP_HIGH_PAUSE）
- severity：风险级别（INFO/WARN/ALERT/CRITICAL）
- recommended_action：建议的动作（例如 PAUSE）
- reason：一段人类可读解释（教学用）
- evidence：用于解释的关键信息（例如 temp_c 与 threshold）
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from cim_worldlab.world.events.event import Event

POLICY_DECISION_TYPE = "POLICY_DECISION"


@dataclass(frozen=True)
class PolicyDecision:
    """
    结构化的决策对象（先不一定直接落盘为文件模型，但便于测试与复用）
    """
    rule_id: str
    severity: str
    recommended_action: str
    reason: str
    evidence: Dict[str, Any]

    def to_event(self, t: int, trace_id: Optional[str] = None) -> Event:
        """
        把 PolicyDecision 包装成统一 Event，进入事件流留痕。

        trace_id：
        - 可选，方便把“输入 → 决策 → 动作”串在一起（后续会更重要）
        """
        payload: Dict[str, Any] = {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "recommended_action": self.recommended_action,
            "reason": self.reason,
            "evidence": self.evidence,
        }
        if trace_id is not None:
            payload["trace_id"] = trace_id

        return Event(t=t, type=POLICY_DECISION_TYPE, payload=payload)
