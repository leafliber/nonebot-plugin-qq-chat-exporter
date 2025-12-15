"""
导出服务：负责从 chatrecorder 获取消息并导出
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from nonebot_plugin_chatrecorder import get_message_records
from nonebot_plugin_orm import get_session
from nonebot_plugin_uninfo import SceneType
from nonebot_plugin_uninfo.orm import SessionModel, UserModel
from sqlalchemy import select

from .converter import convert_records_to_export_messages
from .models import (
    ChatInfo,
    ExportData,
    MessageTypes,
    Resources,
    ResourcesByType,
    SenderStats,
    Statistics,
    TimeRange,
)


async def export_group_messages(
    group_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    output_dir: Optional[str] = None
) -> str:
    """
    导出群聊消息

    Args:
        group_id: 群号
        start_time: 开始时间
        end_time: 结束时间
        output_dir: 输出目录

    Returns:
        输出文件路径
    """
    # 设置默认输出目录
    if output_dir is None:
        output_dir = "exports"

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 获取消息记录
    records = await get_message_records(
        scene_ids=[group_id],
        scene_types=[SceneType.GROUP],
        time_start=start_time,
        time_stop=end_time
    )

    # 获取关联的会话和用户信息
    records_with_info = []
    async with get_session() as db_session:
        for record in records:
            # 获取会话信息
            session_stmt = select(SessionModel).where(
                SessionModel.id == record.session_persist_id
            )
            session = (await db_session.scalars(session_stmt)).first()

            if not session:
                continue

            # 获取用户信息
            user_stmt = select(UserModel).where(
                UserModel.id == session.user_persist_id
            )
            user = (await db_session.scalars(user_stmt)).first()

            if not user:
                continue

            records_with_info.append((record, session, user))

    # 转换消息格式
    export_messages, statistics_data = convert_records_to_export_messages(
        records_with_info, "group", group_id
    )

    # 创建聊天信息
    chat_info = ChatInfo(
        name=f"Group {group_id}",
        type="group"
    )

    # 计算时间范围
    time_range = TimeRange()
    if export_messages:
        # 从第一条和最后一条消息获取时间范围
        first_time = export_messages[0].timestamp
        last_time = export_messages[-1].timestamp

        # 转换为datetime以计算天数
        try:
            dt_first = datetime.fromisoformat(first_time.replace("Z", "+00:00"))
            dt_last = datetime.fromisoformat(last_time.replace("Z", "+00:00"))
            duration_days = (dt_last - dt_first).days

            time_range.start = first_time
            time_range.end = last_time
            time_range.durationDays = duration_days
        except Exception:
            pass

    # 创建统计信息
    total_messages = len(export_messages)
    message_types = MessageTypes(unknown=total_messages)

    # 转换发送者统计
    senders = [
        SenderStats(
            uid=s["uid"],
            name=s["name"],
            messageCount=s["messageCount"],
            percentage=s["percentage"]
        )
        for s in statistics_data["senders"]
    ]

    # 创建资源统计
    resource_stats = statistics_data["resources"]
    resources_by_type = ResourcesByType(
        image=resource_stats["image"],
        video=resource_stats["video"],
        audio=resource_stats["audio"],
        file=resource_stats["file"]
    )
    total_resources = sum(resource_stats.values())
    resources = Resources(
        total=total_resources,
        byType=resources_by_type,
        totalSize=0
    )

    statistics = Statistics(
        totalMessages=total_messages,
        timeRange=time_range,
        messageTypes=message_types,
        senders=senders,
        resources=resources
    )

    # 创建导出数据
    export_data = ExportData(
        chatInfo=chat_info,
        statistics=statistics,
        messages=export_messages
    )

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"group_{group_id}_{timestamp}.json"
    output_file = output_path / filename

    # 写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            export_data.model_dump(mode="json"),
            f,
            ensure_ascii=False,
            indent=2
        )

    return str(output_file)


async def export_private_messages(
    user_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    output_dir: Optional[str] = None
) -> str:
    """
    导出私聊消息

    Args:
        user_id: 用户ID
        start_time: 开始时间
        end_time: 结束时间
        output_dir: 输出目录

    Returns:
        输出文件路径
    """
    # 设置默认输出目录
    if output_dir is None:
        output_dir = "exports"

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 获取消息记录
    records = await get_message_records(
        user_ids=[user_id],
        scene_types=[SceneType.PRIVATE],
        time_start=start_time,
        time_stop=end_time
    )

    # 获取关联的会话和用户信息
    records_with_info = []
    async with get_session() as db_session:
        for record in records:
            # 获取会话信息
            session_stmt = select(SessionModel).where(
                SessionModel.id == record.session_persist_id
            )
            session = (await db_session.scalars(session_stmt)).first()

            if not session:
                continue

            # 获取用户信息
            user_stmt = select(UserModel).where(
                UserModel.id == session.user_persist_id
            )
            user = (await db_session.scalars(user_stmt)).first()

            if not user:
                continue

            records_with_info.append((record, session, user))

    # 转换消息格式
    export_messages, statistics_data = convert_records_to_export_messages(
        records_with_info, "private", user_id
    )

    # 创建聊天信息
    chat_info = ChatInfo(
        name=f"User {user_id}",
        type="private"
    )

    # 计算时间范围
    time_range = TimeRange()
    if export_messages:
        # 从第一条和最后一条消息获取时间范围
        first_time = export_messages[0].timestamp
        last_time = export_messages[-1].timestamp

        # 转换为datetime以计算天数
        try:
            dt_first = datetime.fromisoformat(first_time.replace("Z", "+00:00"))
            dt_last = datetime.fromisoformat(last_time.replace("Z", "+00:00"))
            duration_days = (dt_last - dt_first).days

            time_range.start = first_time
            time_range.end = last_time
            time_range.durationDays = duration_days
        except Exception:
            pass

    # 创建统计信息
    total_messages = len(export_messages)
    message_types = MessageTypes(unknown=total_messages)

    # 转换发送者统计
    senders = [
        SenderStats(
            uid=s["uid"],
            name=s["name"],
            messageCount=s["messageCount"],
            percentage=s["percentage"]
        )
        for s in statistics_data["senders"]
    ]

    # 创建资源统计
    resource_stats = statistics_data["resources"]
    resources_by_type = ResourcesByType(
        image=resource_stats["image"],
        video=resource_stats["video"],
        audio=resource_stats["audio"],
        file=resource_stats["file"]
    )
    total_resources = sum(resource_stats.values())
    resources = Resources(
        total=total_resources,
        byType=resources_by_type,
        totalSize=0
    )

    statistics = Statistics(
        totalMessages=total_messages,
        timeRange=time_range,
        messageTypes=message_types,
        senders=senders,
        resources=resources
    )

    # 创建导出数据
    export_data = ExportData(
        chatInfo=chat_info,
        statistics=statistics,
        messages=export_messages
    )

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"private_{user_id}_{timestamp}.json"
    output_file = output_path / filename

    # 写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            export_data.model_dump(mode="json"),
            f,
            ensure_ascii=False,
            indent=2
        )

    return str(output_file)
