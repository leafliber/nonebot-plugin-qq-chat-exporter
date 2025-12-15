"""
Message exporter functionality
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from .models import (
    ExportData, ChatInfo, Statistics, Message, MessageSender,
    MessageReceiver, MessageContent, MessageStats, Sender,
    TimeRange, MessageTypes, Resources, ResourcesByType,
    ContentResource
)


class ChatExporter:
    """Export chat messages to qq-chat-exporter format"""
    
    def __init__(self):
        self.messages: List[Message] = []
        self.chat_name: str = ""
        self.chat_type: str = "group"
        
    def add_message(
        self,
        message_id: str,
        message_seq: str,
        timestamp: str,
        sender_uid: str,
        sender_name: str,
        receiver_uid: str,
        receiver_type: str,
        content_text: str = "",
        message_type: int = 0,
        is_system: bool = False,
        is_recalled: bool = False,
        sender_uin: Optional[str] = None,
        raw_message: Optional[Dict[str, Any]] = None,
        resources: Optional[List[ContentResource]] = None,
    ) -> None:
        """Add a message to the export"""
        
        # Create message content
        content = MessageContent(
            text=content_text,
            raw=content_text,
            resources=resources or []
        )
        
        # Calculate stats
        stats = MessageStats(
            elementCount=1,
            resourceCount=len(resources) if resources else 0,
            textLength=len(content_text)
        )
        
        # Create message
        msg = Message(
            messageId=message_id,
            messageSeq=message_seq,
            msgRandom="0",
            timestamp=timestamp,
            sender=MessageSender(
                uid=sender_uid,
                uin=sender_uin,
                name=sender_name
            ),
            receiver=MessageReceiver(
                uid=receiver_uid,
                type=receiver_type
            ),
            messageType=message_type,
            isSystemMessage=is_system,
            isRecalled=is_recalled,
            isTempMessage=False,
            content=content,
            stats=stats,
            rawMessage=raw_message
        )
        
        self.messages.append(msg)
    
    def set_chat_info(self, name: str, chat_type: str = "group") -> None:
        """Set chat information"""
        self.chat_name = name
        self.chat_type = chat_type
    
    def _calculate_statistics(self) -> Statistics:
        """Calculate statistics from messages"""
        
        # Count messages by sender
        sender_counts: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"name": "", "count": 0}
        )
        
        # Count resources
        resource_counts = ResourcesByType()
        total_resources = 0
        
        # Process messages
        for msg in self.messages:
            # Count sender messages
            sender_uid = msg.sender.uid
            sender_counts[sender_uid]["name"] = msg.sender.name
            sender_counts[sender_uid]["count"] += 1
            
            # Count resources
            for resource in msg.content.resources:
                total_resources += 1
                if resource.type == "image":
                    resource_counts.image += 1
                elif resource.type == "video":
                    resource_counts.video += 1
                elif resource.type == "audio":
                    resource_counts.audio += 1
                elif resource.type == "file":
                    resource_counts.file += 1
        
        # Create sender statistics
        total_messages = len(self.messages)
        senders = [
            Sender(
                uid=uid,
                name=data["name"],
                messageCount=data["count"],
                percentage=round((data["count"] / total_messages * 100), 2) if total_messages > 0 else 0
            )
            for uid, data in sender_counts.items()
        ]
        
        # Sort senders by message count
        senders.sort(key=lambda x: x.messageCount, reverse=True)
        
        # Calculate time range
        time_range = TimeRange()
        if self.messages:
            timestamps = [msg.timestamp for msg in self.messages]
            time_range.start = min(timestamps)
            time_range.end = max(timestamps)
        
        # Create statistics
        return Statistics(
            totalMessages=total_messages,
            timeRange=time_range,
            messageTypes=MessageTypes(unknown=total_messages),
            senders=senders,
            resources=Resources(
                total=total_resources,
                byType=resource_counts,
                totalSize=0
            )
        )
    
    def export(self, output_path: Optional[str] = None) -> ExportData:
        """Export messages to qq-chat-exporter format"""
        
        # Create chat info
        chat_info = ChatInfo(
            name=self.chat_name or "Exported Chat",
            type=self.chat_type
        )
        
        # Calculate statistics
        statistics = self._calculate_statistics()
        
        # Create export data
        export_data = ExportData(
            chatInfo=chat_info,
            statistics=statistics,
            messages=self.messages
        )
        
        # Save to file if path provided
        if output_path:
            self.save_to_file(export_data, output_path)
        
        return export_data
    
    def save_to_file(self, export_data: ExportData, output_path: str) -> None:
        """Save export data to JSON file"""
        
        # Create output directory if it doesn't exist
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to JSON and save
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(
                export_data.model_dump(by_alias=True),
                f,
                ensure_ascii=False,
                indent=2
            )
    
    def clear(self) -> None:
        """Clear all messages"""
        self.messages.clear()
