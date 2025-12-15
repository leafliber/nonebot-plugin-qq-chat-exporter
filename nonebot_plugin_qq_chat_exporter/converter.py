"""
消息转换器：将 chatrecorder 格式转换为 qq-chat-exporter 格式
"""
import logging
import time
from datetime import datetime
from typing import Any

from nonebot_plugin_chatrecorder import MessageRecord
from nonebot_plugin_uninfo.orm import SessionModel, UserModel

from .models import (
    ExportMessage,
    MessageContent,
    MessageReceiver,
    MessageSender,
    MessageStats,
)

logger = logging.getLogger(__name__)


def parse_message_content(message_data: list[dict[str, Any]]) -> tuple[MessageContent, str, dict]:
    """
    解析消息内容

    Args:
        message_data: OneBot 消息段列表

    Returns:
        (消息内容, 纯文本, 资源统计字典)
    """
    text_parts = []
    resources = []
    resource_stats = {"image": 0, "video": 0, "audio": 0, "file": 0}
    element_count = 0

    for segment in message_data:
        seg_type = segment.get("type", "text")
        seg_data = segment.get("data", {})
        element_count += 1

        # 构建文本
        if seg_type == "text":
            text_parts.append(seg_data.get("text", ""))
        elif seg_type == "face":
            text_parts.append(f"[表情{seg_data.get('id', '')}]")
        elif seg_type == "image":
            text_parts.append("[图片]")
            resource_stats["image"] += 1
            resources.append({"type": "image", "data": seg_data})
        elif seg_type == "video":
            text_parts.append("[视频]")
            resource_stats["video"] += 1
            resources.append({"type": "video", "data": seg_data})
        elif seg_type == "audio" or seg_type == "record":
            text_parts.append("[语音]")
            resource_stats["audio"] += 1
            resources.append({"type": "audio", "data": seg_data})
        elif seg_type == "file":
            text_parts.append(f"[文件: {seg_data.get('file', '')}]")
            resource_stats["file"] += 1
            resources.append({"type": "file", "data": seg_data})
        elif seg_type == "at":
            qq = seg_data.get("qq", "")
            if qq == "all":
                text_parts.append("@全体成员")
            else:
                text_parts.append(f"@{qq}")
        elif seg_type == "reply":
            text_parts.append("[回复]")
        elif seg_type == "forward":
            text_parts.append("[转发消息]")
        else:
            text_parts.append(f"[{seg_type}]")

    text = "".join(text_parts)
    content = MessageContent(
        text=text,
        raw=text,
        resources=resources
    )

    return content, text, resource_stats


def convert_records_to_export_messages(
    records: list[tuple[MessageRecord, SessionModel, UserModel]],
    chat_type: str,
    chat_id: str
) -> tuple[list[ExportMessage], dict[str, Any]]:
    """
    批量转换消息记录

    Args:
        records: (消息记录, 会话模型, 用户模型) 元组列表
        chat_type: 聊天类型 ("group" or "private")
        chat_id: 聊天ID

    Returns:
        (导出消息列表, 统计信息字典)
    """
    export_messages = []
    sender_stats = {}
    resource_totals = {"image": 0, "video": 0, "audio": 0, "file": 0}
    failed_count = 0

    for record, session, user in records:
        try:
            # 验证 record 对象的必要属性
            if not hasattr(record, 'message'):
                logger.warning(
                    "Message record %s missing 'message' attribute, skipping",
                    getattr(record, "message_id", "unknown")
                )
                failed_count += 1
                continue

            # 解析消息内容
            message_data = record.message if isinstance(record.message, list) else []
            
            # 如果 message_data 为空或无效，记录并跳过
            if not message_data:
                logger.debug(
                    "Message %s has empty message_data, creating minimal export",
                    getattr(record, "message_id", "unknown")
                )
            
            content, text, resource_stats = parse_message_content(message_data)

            # 更新资源统计
            for key in resource_totals:
                resource_totals[key] += resource_stats[key]

            # 构建发送者信息
            # 增加对用户属性的防御性检查
            user_id = getattr(user, 'user_id', 'unknown')
            sender_uid = f"u_{user_id}"
            sender_name = getattr(user, 'user_name', None) or ""
            sender = MessageSender(
                uid=sender_uid,
                uin=str(user_id),
                name=sender_name
            )

            # 更新发送者统计
            if sender_uid not in sender_stats:
                sender_stats[sender_uid] = {
                    "uid": sender_uid,
                    "name": sender_name,
                    "messageCount": 0
                }
            sender_stats[sender_uid]["messageCount"] += 1

            # 构建接收者信息
            receiver = MessageReceiver(
                uid=str(chat_id),
                type=chat_type
            )

            # 转换时间戳为ISO格式
            # 增加对时间属性的防御性检查
            if hasattr(record, 'time') and record.time:
                timestamp = record.time.isoformat(timespec="milliseconds") + "Z"
            else:
                logger.warning(
                    "Message %s missing time attribute, using current time",
                    getattr(record, "message_id", "unknown")
                )
                timestamp = datetime.now().isoformat(timespec="milliseconds") + "Z"

            # 构建消息统计
            stats = MessageStats(
                elementCount=len(message_data),
                resourceCount=sum(resource_stats.values()),
                textLength=len(text),
                processingTime=0
            )

            # 判断是否为系统消息
            # 根据消息类型判断，一般 record.type 为 "message" 是普通消息
            is_system_message = getattr(record, 'type', 'message') != "message"

            # 获取消息ID，如果不存在则生成一个基于时间戳的唯一ID
            message_id = getattr(record, 'message_id', None)
            if not message_id:
                # 使用纳秒时间戳作为唯一ID，确保不同记录不会产生相同ID
                message_id = f"msg_{int(time.time() * 1000000)}"
                logger.debug(f"Generated fallback message_id: {message_id}")

            # 构建导出消息
            export_msg = ExportMessage(
                messageId=str(message_id),
                messageSeq="",
                msgRandom="0",
                timestamp=timestamp,
                sender=sender,
                receiver=receiver,
                messageType=5,
                isSystemMessage=is_system_message,
                isRecalled=False,
                isTempMessage=False,
                content=content,
                stats=stats,
                rawMessage=None  # 可选字段，默认为None
            )

            export_messages.append(export_msg)
        except (KeyError, AttributeError, ValueError) as e:
            # 记录转换失败的消息，包含详细错误信息
            failed_count += 1
            logger.warning(
                "Failed to convert message %s: %s - %s",
                getattr(record, "message_id", "unknown"),
                type(e).__name__,
                str(e)
            )
            continue
        except Exception as e:
            # 捕获其他未预期的异常
            failed_count += 1
            logger.error(
                "Unexpected error converting message %s: %s - %s",
                getattr(record, "message_id", "unknown"),
                type(e).__name__,
                str(e),
                exc_info=True
            )
            continue

    # 记录处理结果
    if failed_count > 0:
        logger.info(
            "Conversion completed: %d succeeded, %d failed out of %d total",
            len(export_messages),
            failed_count,
            len(records)
        )

    # 计算发送者统计百分比
    total_messages = len(export_messages)
    sender_list = []
    for uid, stats_data in sender_stats.items():
        percentage = (stats_data["messageCount"] / total_messages * 100) if total_messages > 0 else 0
        sender_list.append({
            "uid": uid,
            "name": stats_data["name"],
            "messageCount": stats_data["messageCount"],
            "percentage": round(percentage, 2)
        })

    statistics = {
        "senders": sender_list,
        "resources": resource_totals
    }

    return export_messages, statistics
