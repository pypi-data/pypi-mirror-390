"""客户端配置模块"""
from client.config.settings import ClientSettings, get_settings

# 导出全局配置实例
settings = ClientSettings()

__all__ = ["settings", "ClientSettings", "get_settings"]

