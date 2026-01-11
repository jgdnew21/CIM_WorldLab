"""
state 包导出：
- WorldState：世界状态
- apply_event / apply_events：状态推导规则（reducer）
"""
from .world_state import WorldState
from .reducer import apply_event, apply_events

__all__ = ["WorldState", "apply_event", "apply_events"]
