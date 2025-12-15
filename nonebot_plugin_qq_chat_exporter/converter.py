"""
消息转换器：将 chatrecorder 格式转换为 qq-chat-exporter 格式
"""
from typing import Any

from nonebot_plugin_chatrecorder import MessageRecord
from nonebot_plugin_uninfo.orm import SessionModel, UserModel

from .models import ExportMessage, MessageElement, SenderInfo


def parse_message_elements(message_data: list[dict[str, Any]]) -> tuple[list[MessageElement], str]:
    """
    解析消息元素

    Args:
        message_data: OneBot 消息段列表

    Returns:
        (元素列表, 原始消息文本)
    """
    elements = []
    raw_parts = []

    for segment in message_data:
        seg_type = segment.get("type", "text")
        seg_data = segment.get("data", {})

        # 构建元素
        element = MessageElement(type=seg_type, data=seg_data)
        elements.append(element)

        # 构建原始消息文本
        if seg_type == "text":
            raw_parts.append(seg_data.get("text", ""))
        elif seg_type == "face":
            raw_parts.append(f"[表情{seg_data.get('id', '')}]")
        elif seg_type == "image":
            raw_parts.append("[图片]")
        elif seg_type == "video":
            raw_parts.append("[视频]")
        elif seg_type == "audio" or seg_type == "record":
            raw_parts.append("[语音]")
        elif seg_type == "file":
            raw_parts.append(f"[文件: {seg_data.get('file', '')}]")
        elif seg_type == "at":
            qq = seg_data.get("qq", "")
            if qq == "all":
                raw_parts.append("@全体成员")
            else:
                raw_parts.append(f"@{qq}")
        elif seg_type == "reply":
            raw_parts.append("[回复]")
        elif seg_type == "forward":
            raw_parts.append("[转发消息]")
        else:
            raw_parts.append(f"[{seg_type}]")

    raw_message = "".join(raw_parts)
    return elements, raw_message


async def convert_record_to_export_message(
    record: MessageRecord,
    session: SessionModel,
    user: UserModel
) -> ExportMessage:
    """
    将 MessageRecord 转换为 ExportMessage

    Args:
        record: 消息记录
        session: 会话模型
        user: 用户模型

    Returns:
        导出消息
    """
    # 解析消息内容
    message_data = record.message if isinstance(record.message, list) else []
    elements, raw_message = parse_message_elements(message_data)

    # 构建发送者信息
    sender = SenderInfo(
        user_id=user.user_id,
        nickname=user.user_name or "",
        card="",  # chatrecorder 不存储群名片，留空
        role="member"
    )

    # 转换时间戳（转为秒）
    timestamp = int(record.time.timestamp())

    # 构建导出消息
    export_msg = ExportMessage(
        message_id=record.message_id,
        message_seq=None,  # chatrecorder 不存储序列号
        message_type=record.type,
        time=timestamp,
        sender=sender,
        elements=elements,
        raw_message=raw_message,
        plain_text=record.plain_text
    )

    return export_msg


def convert_records_to_export_messages(
    records: list[tuple[MessageRecord, SessionModel, UserModel]]
) -> list[ExportMessage]:
    """
    批量转换消息记录

    Args:
        records: (消息记录, 会话模型, 用户模型) 元组列表

    Returns:
        导出消息列表
    """
    export_messages = []

    for record, session, user in records:
        try:
            # 解析消息内容
            message_data = record.message if isinstance(record.message, list) else []
            elements, raw_message = parse_message_elements(message_data)

            # 构建发送者信息
            sender = SenderInfo(
                user_id=user.user_id,
                nickname=user.user_name or "",
                card="",
                role="member"
            )

            # 转换时间戳
            timestamp = int(record.time.timestamp())

            # 构建导出消息
            export_msg = ExportMessage(
                message_id=record.message_id,
                message_seq=None,
                message_type=record.type,
                time=timestamp,
                sender=sender,
                elements=elements,
                raw_message=raw_message,
                plain_text=record.plain_text
            )

            export_messages.append(export_msg)
        except Exception:
            # 记录转换失败的消息，但继续处理其他消息
            # 静默跳过，避免打印敏感信息
            continue

    return export_messages
