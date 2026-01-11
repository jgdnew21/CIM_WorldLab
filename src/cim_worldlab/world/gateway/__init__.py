"""
gateway 包：世界对外的“口子”

接口：
- PluginGateway：runtime 依赖的抽象接口

实现：
- FakePluginGateway：测试替身（内存队列）
- FileQueueGateway：真实实现（文件队列，跨进程）
"""
from .plugin_gateway import PluginGateway, FakePluginGateway
from .file_queue_gateway import FileQueueGateway

__all__ = ["PluginGateway", "FakePluginGateway", "FileQueueGateway"]
