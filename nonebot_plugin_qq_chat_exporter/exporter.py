"""
导出服务：负责从 chatrecorder 获取消息并导出
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from nonebot_plugin_chatrecorder import get_message_records, MessageRecord
from nonebot_plugin_orm import get_session
from nonebot_plugin_uninfo import SceneType
from nonebot_plugin_uninfo.orm import SessionModel, UserModel, SceneModel, BotModel
from sqlalchemy import select

from .converter import convert_records_to_export_messages
from .models import ExportData, ExportMetadata


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
    export_messages = convert_records_to_export_messages(records_with_info)
    
    # 计算时间范围
    time_range = {}
    if export_messages:
        time_range["start"] = min(msg.time for msg in export_messages)
        time_range["end"] = max(msg.time for msg in export_messages)
    
    # 创建元数据
    metadata = ExportMetadata(
        export_time=datetime.now(),
        exporter="nonebot-plugin-qq-chat-exporter",
        version="0.1.0",
        chat_type="group",
        chat_id=group_id,
        chat_name=f"Group {group_id}",
        message_count=len(export_messages),
        time_range=time_range
    )
    
    # 创建导出数据
    export_data = ExportData(
        metadata=metadata,
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
    export_messages = convert_records_to_export_messages(records_with_info)
    
    # 计算时间范围
    time_range = {}
    if export_messages:
        time_range["start"] = min(msg.time for msg in export_messages)
        time_range["end"] = max(msg.time for msg in export_messages)
    
    # 创建元数据
    metadata = ExportMetadata(
        export_time=datetime.now(),
        exporter="nonebot-plugin-qq-chat-exporter",
        version="0.1.0",
        chat_type="private",
        chat_id=user_id,
        chat_name=f"User {user_id}",
        message_count=len(export_messages),
        time_range=time_range
    )
    
    # 创建导出数据
    export_data = ExportData(
        metadata=metadata,
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
