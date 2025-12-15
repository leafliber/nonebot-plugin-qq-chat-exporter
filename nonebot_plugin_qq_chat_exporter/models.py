"""
兼容 qq-chat-exporter 的数据模型
"""
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageElementType(str, Enum):
    """消息元素类型"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    FACE = "face"
    AT = "at"
    REPLY = "reply"
    FORWARD = "forward"
    JSON = "json"
    XML = "xml"


class MessageElement(BaseModel):
    """消息元素"""
    type: str
    data: dict[str, Any] = Field(default_factory=dict)


class SenderInfo(BaseModel):
    """发送者信息"""
    user_id: str
    nickname: str = ""
    card: str = ""
    role: str = "member"


class ExportMessage(BaseModel):
    """导出的消息格式（兼容 qq-chat-exporter）"""
    message_id: str
    message_seq: Optional[str] = None
    message_type: str  # "message" or "message_sent"
    time: int  # Unix timestamp in seconds
    sender: SenderInfo
    elements: list[MessageElement] = Field(default_factory=list)
    raw_message: str = ""
    plain_text: str = ""


class ExportMetadata(BaseModel):
    """导出元数据"""
    export_time: datetime = Field(default_factory=datetime.now)
    exporter: str = "nonebot-plugin-qq-chat-exporter"
    version: str = "0.1.0"
    chat_type: str  # "group" or "private"
    chat_id: str
    chat_name: str = ""
    message_count: int = 0
    time_range: dict[str, Optional[int]] = Field(default_factory=dict)


class ExportData(BaseModel):
    """完整导出数据"""
    metadata: ExportMetadata
    messages: list[ExportMessage] = Field(default_factory=list)
