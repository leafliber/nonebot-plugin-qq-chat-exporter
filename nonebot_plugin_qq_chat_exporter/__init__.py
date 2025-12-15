"""
NoneBot plugin for exporting QQ chat messages in qq-chat-exporter format
"""
try:
    from nonebot import get_driver, on_command
    from nonebot.plugin import PluginMetadata
    from nonebot.adapters import Bot, Event
    from nonebot.params import CommandArg
    from nonebot.typing import T_State
    from nonebot.adapters.onebot.v11 import (
        Bot as OneBotV11Bot,
        GroupMessageEvent,
        PrivateMessageEvent,
        Message,
        MessageSegment,
    )
    NONEBOT_AVAILABLE = True
except ImportError:
    NONEBOT_AVAILABLE = False

from pathlib import Path
from datetime import datetime
from typing import Optional

from .config import Config
from .exporter import ChatExporter
from .models import ContentResource

# Only define plugin metadata if NoneBot is available
if NONEBOT_AVAILABLE:
    __plugin_meta__ = PluginMetadata(
        name="QQ Chat Exporter",
        description="兼容qq-chat-exporter格式的QQ消息导出插件",
        usage="使用命令 /export 开始导出当前会话的消息",
        type="application",
        homepage="https://github.com/leafliber/nonebot-plugin-qq-chat-exporter",
        config=Config,
        supported_adapters={"~onebot.v11"},
    )

    # Load config
    plugin_config = Config.parse_obj(get_driver().config)

    # Store exporters for different chats
    exporters = {}

    # Command: start export
    export_cmd = on_command("export", aliases={"导出"}, priority=5, block=True)


    @export_cmd.handle()
    async def handle_export(bot: Bot, event: Event, state: T_State):
        """Handle export command"""
        
        # Get chat ID
        if isinstance(event, GroupMessageEvent):
            chat_id = f"group_{event.group_id}"
            chat_name = str(event.group_id)
            chat_type = "group"
        elif isinstance(event, PrivateMessageEvent):
            chat_id = f"private_{event.user_id}"
            chat_name = str(event.user_id)
            chat_type = "private"
        else:
            await export_cmd.finish("暂不支持此类型的会话导出")
            return
        
        # Create or get exporter
        if chat_id not in exporters:
            exporter = ChatExporter()
            exporter.set_chat_info(chat_name, chat_type)
            exporters[chat_id] = exporter
        
        await export_cmd.send("开始导出消息，请继续发送消息或使用 /export_finish 完成导出")


    # Command: add message to export
    record_cmd = on_command("export_record", priority=5, block=False)


    # Command: finish export
    finish_cmd = on_command("export_finish", aliases={"完成导出"}, priority=5, block=True)


    @finish_cmd.handle()
    async def handle_finish(bot: Bot, event: Event):
        """Handle finish export command"""
        
        # Get chat ID
        if isinstance(event, GroupMessageEvent):
            chat_id = f"group_{event.group_id}"
        elif isinstance(event, PrivateMessageEvent):
            chat_id = f"private_{event.user_id}"
        else:
            await finish_cmd.finish("暂不支持此类型的会话")
            return
        
        # Get exporter
        exporter = exporters.get(chat_id)
        if not exporter:
            await finish_cmd.finish("未找到导出任务，请先使用 /export 开始导出")
            return
        
        # Export messages
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(plugin_config.qq_chat_exporter_output_dir)
        output_file = output_dir / f"export_{chat_id}_{timestamp}.json"
        
        export_data = exporter.export(str(output_file))
        
        # Clear exporter
        del exporters[chat_id]
        
        await finish_cmd.finish(
            f"导出完成！\n"
            f"共导出 {export_data.statistics.totalMessages} 条消息\n"
            f"文件保存在: {output_file}"
        )


    def _extract_resources(message: Message) -> list[ContentResource]:
        """Extract resources from message"""
        resources = []
        
        for seg in message:
            if seg.type == "image":
                resources.append(ContentResource(
                    type="image",
                    url=seg.data.get("url", ""),
                    filename=seg.data.get("file", "")
                ))
            elif seg.type == "video":
                resources.append(ContentResource(
                    type="video",
                    url=seg.data.get("url", ""),
                    filename=seg.data.get("file", "")
                ))
            elif seg.type == "record":
                resources.append(ContentResource(
                    type="audio",
                    url=seg.data.get("url", ""),
                    filename=seg.data.get("file", "")
                ))
            elif seg.type == "file":
                resources.append(ContentResource(
                    type="file",
                    url=seg.data.get("url", ""),
                    filename=seg.data.get("file", "")
                ))
        
        return resources


__all__ = [
    "ChatExporter",
    "Config",
]

# Only export plugin metadata if NoneBot is available
if NONEBOT_AVAILABLE:
    __all__.append("__plugin_meta__")
