"""
NoneBot QQ Chat Exporter Plugin

导出 QQ 聊天记录为兼容 qq-chat-exporter 的 JSON 格式
"""
from nonebot import require
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_chatrecorder")

from . import webui  # noqa: F401
from .exporter import export_group_messages, export_private_messages  # noqa: F401

__plugin_meta__ = PluginMetadata(
    name="QQ聊天记录导出",
    description="导出QQ聊天记录为兼容qq-chat-exporter的JSON格式",
    usage=(
        "访问 WebUI 进行操作:\n"
        "http://your-host:port/qq-chat-exporter\n\n"
        "或通过 API 调用:\n"
        "POST /qq-chat-exporter/export\n"
        "{\n"
        '  "chat_type": "group",\n'
        '  "chat_id": "123456789",\n'
        '  "start_time": "2024-01-01T00:00:00",\n'
        '  "end_time": "2024-12-31T23:59:59"\n'
        "}"
    ),
    type="application",
    homepage="https://github.com/leafliber/nonebot-plugin-qq-chat-exporter",
    supported_adapters={"~onebot.v11", "~onebot.v12"},
    extra={
        "author": "leafliber",
        "version": "0.1.0",
    },
)

__version__ = "0.1.0"

__all__ = [
    "__plugin_meta__",
    "__version__",
    "export_group_messages",
    "export_private_messages",
]
