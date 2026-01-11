"""
gateway 包：世界对外的“口子”
- PluginGateway：接口（协议）
- FakePluginGateway：测试替身

未来会新增：
- HttpPluginGateway：真实 HTTP/JSON 实现
"""
from .plugin_gateway import PluginGateway, FakePluginGateway

__all__ = ["PluginGateway", "FakePluginGateway"]
