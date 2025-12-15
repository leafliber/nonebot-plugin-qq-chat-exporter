"""
Data models for qq-chat-exporter format
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class Metadata(BaseModel):
    """Export metadata"""
    name: str = "exporter"
    copyright: str = ""
    version: str = "4.0.0"


class ChatInfo(BaseModel):
    """Chat information"""
    name: str
    type: str  # "private" or "group"


class Sender(BaseModel):
    """Sender statistics"""
    uid: str
    name: str
    messageCount: int = Field(alias="messageCount")
    percentage: float


class TimeRange(BaseModel):
    """Time range for messages"""
    start: str = ""
    end: str = ""
    durationDays: int = 0


class MessageTypes(BaseModel):
    """Message type statistics"""
    unknown: int = 0


class ResourcesByType(BaseModel):
    """Resources by type"""
    image: int = 0
    video: int = 0
    audio: int = 0
    file: int = 0


class Resources(BaseModel):
    """Resource statistics"""
    total: int = 0
    byType: ResourcesByType = Field(default_factory=ResourcesByType)
    totalSize: int = 0


class Statistics(BaseModel):
    """Chat statistics"""
    totalMessages: int
    timeRange: TimeRange = Field(default_factory=TimeRange)
    messageTypes: MessageTypes = Field(default_factory=MessageTypes)
    senders: List[Sender] = Field(default_factory=list)
    resources: Resources = Field(default_factory=Resources)


class MessageSender(BaseModel):
    """Message sender information"""
    uid: str
    uin: Optional[str] = None
    name: str


class MessageReceiver(BaseModel):
    """Message receiver information"""
    uid: str
    type: str  # "group" or "private"


class ContentResource(BaseModel):
    """Content resource (image, video, etc.)"""
    type: str
    url: Optional[str] = None
    size: Optional[int] = None
    filename: Optional[str] = None


class MessageContent(BaseModel):
    """Message content"""
    text: str = ""
    html: str = ""
    raw: str = ""
    mentions: List[str] = Field(default_factory=list)
    resources: List[ContentResource] = Field(default_factory=list)
    emojis: List[Any] = Field(default_factory=list)
    special: List[Any] = Field(default_factory=list)


class MessageStats(BaseModel):
    """Message statistics"""
    elementCount: int = 0
    resourceCount: int = 0
    textLength: int = 0
    processingTime: int = 0


class Message(BaseModel):
    """Message data"""
    messageId: str
    messageSeq: str
    msgRandom: str
    timestamp: str
    sender: MessageSender
    receiver: MessageReceiver
    messageType: int
    isSystemMessage: bool = False
    isRecalled: bool = False
    isTempMessage: bool = False
    content: MessageContent
    stats: MessageStats = Field(default_factory=MessageStats)
    rawMessage: Optional[Dict[str, Any]] = None


class ExportFilters(BaseModel):
    """Export filters"""
    pass


class ExportOptionsData(BaseModel):
    """Export options data"""
    includeResourceLinks: bool = True
    includeSystemMessages: bool = True
    timeFormat: str = "YYYY-MM-DD HH:mm:ss"
    encoding: str = "utf-8"


class ExportOptions(BaseModel):
    """Export options"""
    includedFields: List[str] = Field(
        default_factory=lambda: ["id", "timestamp", "sender", "content", "resources"]
    )
    filters: ExportFilters = Field(default_factory=ExportFilters)
    options: ExportOptionsData = Field(default_factory=ExportOptionsData)


class ExportData(BaseModel):
    """Complete export data structure"""
    metadata: Metadata = Field(default_factory=Metadata)
    chatInfo: ChatInfo
    statistics: Statistics
    messages: List[Message]
    exportOptions: ExportOptions = Field(default_factory=ExportOptions)
