"""
兼容 qq-chat-exporter 的数据模型
"""
from typing import Any, Optional

from pydantic import BaseModel, Field


# New models for v4.0.0 format
class Metadata(BaseModel):
    """元数据"""
    name: str = "exporter"
    copyright: str = ""
    version: str = "4.0.0"


class ChatInfo(BaseModel):
    """聊天信息"""
    name: str
    type: str  # "group" or "private"


class TimeRange(BaseModel):
    """时间范围"""
    start: str = ""
    end: str = ""
    durationDays: int = 0


class MessageTypes(BaseModel):
    """消息类型统计"""
    unknown: int = 0


class SenderStats(BaseModel):
    """发送者统计"""
    uid: str
    name: str
    messageCount: int
    percentage: float


class ResourcesByType(BaseModel):
    """资源类型统计"""
    image: int = 0
    video: int = 0
    audio: int = 0
    file: int = 0


class Resources(BaseModel):
    """资源统计"""
    total: int = 0
    byType: ResourcesByType = Field(default_factory=ResourcesByType)
    totalSize: int = 0


class Statistics(BaseModel):
    """统计信息"""
    totalMessages: int = 0
    timeRange: TimeRange = Field(default_factory=TimeRange)
    messageTypes: MessageTypes = Field(default_factory=MessageTypes)
    senders: list[SenderStats] = Field(default_factory=list)
    resources: Resources = Field(default_factory=Resources)


class MessageSender(BaseModel):
    """消息发送者"""
    uid: str
    uin: str = ""
    name: str


class MessageReceiver(BaseModel):
    """消息接收者"""
    uid: str
    type: str  # "group" or "private"


class MessageContent(BaseModel):
    """消息内容"""
    text: str = ""
    html: str = ""
    raw: str = ""
    mentions: list[Any] = Field(default_factory=list)
    resources: list[Any] = Field(default_factory=list)
    emojis: list[Any] = Field(default_factory=list)
    special: list[Any] = Field(default_factory=list)


class MessageStats(BaseModel):
    """消息统计"""
    elementCount: int = 0
    resourceCount: int = 0
    textLength: int = 0
    processingTime: int = 0


class ExportMessage(BaseModel):
    """导出的消息格式"""
    messageId: str
    messageSeq: str = ""
    msgRandom: str = "0"
    timestamp: str  # ISO 8601 format
    sender: MessageSender
    receiver: MessageReceiver
    messageType: int = 5
    isSystemMessage: bool = True
    isRecalled: bool = False
    isTempMessage: bool = False
    content: MessageContent = Field(default_factory=MessageContent)
    stats: MessageStats = Field(default_factory=MessageStats)
    rawMessage: Optional[dict[str, Any]] = None


class ExportOptions(BaseModel):
    """导出选项"""
    includedFields: list[str] = Field(
        default_factory=lambda: ["id", "timestamp", "sender", "content", "resources"]
    )
    filters: dict[str, Any] = Field(default_factory=dict)
    options: dict[str, Any] = Field(
        default_factory=lambda: {
            "includeResourceLinks": True,
            "includeSystemMessages": True,
            "timeFormat": "YYYY-MM-DD HH:mm:ss",
            "encoding": "utf-8"
        }
    )


class ExportData(BaseModel):
    """完整导出数据"""
    metadata: Metadata = Field(default_factory=Metadata)
    chatInfo: ChatInfo
    statistics: Statistics = Field(default_factory=Statistics)
    messages: list[ExportMessage] = Field(default_factory=list)
    exportOptions: ExportOptions = Field(default_factory=ExportOptions)
