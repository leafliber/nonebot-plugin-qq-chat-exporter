"""
导出服务：负责从 chatrecorder 获取消息并导出
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from nonebot_plugin_chatrecorder import get_message_records, MessageRecord
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

logger = logging.getLogger(__name__)


async def _load_records_with_info(records: list[MessageRecord]):
    """
    批量加载消息记录及其关联的会话和用户信息
    
    Args:
        records: 消息记录列表
        
    Returns:
        (消息记录, 会话模型, 用户模型) 元组列表
    """
    if not records:
        return []
    
    logger.info(f"Loading info for {len(records)} message records")
    
    records_with_info = []
    
    # 收集所有需要查询的session_persist_id（使用set去重）
    session_ids = list({r.session_persist_id for r in records if hasattr(r, 'session_persist_id')})
    
    if not session_ids:
        logger.warning("No valid session IDs found in records")
        return []
    
    async with get_session() as db_session:
        # 批量查询所有会话信息
        logger.debug(f"Batch loading {len(session_ids)} sessions")
        sessions_stmt = select(SessionModel).where(SessionModel.id.in_(session_ids))
        sessions_result = await db_session.scalars(sessions_stmt)
        sessions_dict = {s.id: s for s in sessions_result.all()}
        
        # 收集所有需要查询的user_persist_id（使用set去重）
        user_ids = list({
            s.user_persist_id 
            for s in sessions_dict.values() 
            if hasattr(s, 'user_persist_id')
        })
        
        if not user_ids:
            logger.warning("No valid user IDs found in sessions")
            return []
        
        # 批量查询所有用户信息
        logger.debug(f"Batch loading {len(user_ids)} users")
        users_stmt = select(UserModel).where(UserModel.id.in_(user_ids))
        users_result = await db_session.scalars(users_stmt)
        users_dict = {u.id: u for u in users_result.all()}
    
    # 组装结果
    skipped = 0
    for record in records:
        if not hasattr(record, 'session_persist_id'):
            skipped += 1
            continue
            
        session = sessions_dict.get(record.session_persist_id)
        if not session:
            skipped += 1
            continue
        
        if not hasattr(session, 'user_persist_id'):
            skipped += 1
            continue
            
        user = users_dict.get(session.user_persist_id)
        if not user:
            skipped += 1
            continue
        
        records_with_info.append((record, session, user))
    
    if skipped > 0:
        logger.warning(f"Skipped {skipped} records due to missing session or user info")
    
    logger.info(f"Successfully loaded info for {len(records_with_info)} records")
    return records_with_info


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
    try:
        # 设置默认输出目录
        if output_dir is None:
            output_dir = "exports"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting export for group {group_id}")

        # 获取消息记录
        records = await get_message_records(
            scene_ids=[group_id],
            scene_types=[SceneType.GROUP],
            time_start=start_time,
            time_stop=end_time
        )

        logger.info(f"Retrieved {len(records)} message records")

        if not records:
            logger.warning(f"No messages found for group {group_id}")
            # 仍然创建空的导出文件
            records_with_info = []
        else:
            # 使用批量加载获取关联信息
            records_with_info = await _load_records_with_info(records)

        # 转换消息格式
        logger.info("Converting messages to export format")
        export_messages, statistics_data = convert_records_to_export_messages(
            records_with_info, "group", group_id
        )

        logger.info(f"Converted {len(export_messages)} messages successfully")

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
            except Exception as e:
                logger.warning(f"Failed to calculate time range: {e}")

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
        logger.info(f"Writing export to {output_file}")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                export_data.model_dump(mode="json"),
                f,
                ensure_ascii=False,
                indent=2
            )

        logger.info(f"Export completed successfully: {output_file}")
        return str(output_file)
    
    except Exception as e:
        logger.error(f"Failed to export group messages: {type(e).__name__} - {str(e)}", exc_info=True)
        raise


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
    try:
        # 设置默认输出目录
        if output_dir is None:
            output_dir = "exports"

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting export for user {user_id}")

        # 获取消息记录
        records = await get_message_records(
            user_ids=[user_id],
            scene_types=[SceneType.PRIVATE],
            time_start=start_time,
            time_stop=end_time
        )

        logger.info(f"Retrieved {len(records)} message records")

        if not records:
            logger.warning(f"No messages found for user {user_id}")
            # 仍然创建空的导出文件
            records_with_info = []
        else:
            # 使用批量加载获取关联信息
            records_with_info = await _load_records_with_info(records)

        # 转换消息格式
        logger.info("Converting messages to export format")
        export_messages, statistics_data = convert_records_to_export_messages(
            records_with_info, "private", user_id
        )

        logger.info(f"Converted {len(export_messages)} messages successfully")

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
            except Exception as e:
                logger.warning(f"Failed to calculate time range: {e}")

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
        logger.info(f"Writing export to {output_file}")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                export_data.model_dump(mode="json"),
                f,
                ensure_ascii=False,
                indent=2
            )

        logger.info(f"Export completed successfully: {output_file}")
        return str(output_file)
    
    except Exception as e:
        logger.error(f"Failed to export private messages: {type(e).__name__} - {str(e)}", exc_info=True)
        raise
