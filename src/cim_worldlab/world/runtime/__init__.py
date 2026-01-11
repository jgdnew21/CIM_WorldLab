"""
runtime 子包导出：
- WorldRuntime：世界会动的心脏
- EventLog：内存事件日志（调试/教学用）
"""
from .runtime import WorldRuntime
from .event_log import EventLog

__all__ = ["WorldRuntime", "EventLog"]
