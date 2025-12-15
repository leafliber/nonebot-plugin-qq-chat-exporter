"""
独立测试 - 测试核心功能而不依赖 NoneBot
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime

from nonebot_plugin_qq_chat_exporter.models import (
    ExportData,
    ExportMessage,
    ExportMetadata,
    MessageElement,
    SenderInfo,
)


def test_message_element():
    """测试消息元素模型"""
    element = MessageElement(type="text", data={"text": "Hello"})
    assert element.type == "text"
    assert element.data["text"] == "Hello"
    print("✓ MessageElement model works")


def test_sender_info():
    """测试发送者信息模型"""
    sender = SenderInfo(
        user_id="123456",
        nickname="测试用户",
        card="群名片",
        role="admin"
    )
    assert sender.user_id == "123456"
    assert sender.nickname == "测试用户"
    assert sender.card == "群名片"
    assert sender.role == "admin"
    print("✓ SenderInfo model works")


def test_export_message():
    """测试导出消息模型"""
    sender = SenderInfo(user_id="123", nickname="User")
    message = ExportMessage(
        message_id="msg_001",
        message_type="message",
        time=1704067200,
        sender=sender,
        elements=[
            MessageElement(type="text", data={"text": "测试消息"}),
            MessageElement(type="image", data={"url": "http://example.com/img.jpg"})
        ],
        raw_message="测试消息[图片]",
        plain_text="测试消息"
    )
    assert message.message_id == "msg_001"
    assert message.sender.user_id == "123"
    assert len(message.elements) == 2
    assert message.elements[0].type == "text"
    assert message.elements[1].type == "image"
    print("✓ ExportMessage model works")


def test_export_metadata():
    """测试导出元数据模型"""
    metadata = ExportMetadata(
        export_time=datetime(2024, 12, 15, 12, 0, 0),
        exporter="test-exporter",
        version="1.0.0",
        chat_type="group",
        chat_id="789012",
        chat_name="测试群聊",
        message_count=100,
        time_range={"start": 1704067200, "end": 1704153600}
    )
    assert metadata.chat_type == "group"
    assert metadata.chat_id == "789012"
    assert metadata.message_count == 100
    assert metadata.time_range["start"] == 1704067200
    print("✓ ExportMetadata model works")


def test_export_data():
    """测试完整导出数据模型"""
    metadata = ExportMetadata(
        chat_type="private",
        chat_id="123456",
        message_count=2
    )
    
    sender1 = SenderInfo(user_id="123", nickname="Alice")
    sender2 = SenderInfo(user_id="456", nickname="Bob")
    
    messages = [
        ExportMessage(
            message_id="msg1",
            message_type="message",
            time=1704067200,
            sender=sender1,
            elements=[MessageElement(type="text", data={"text": "Hi"})],
            raw_message="Hi",
            plain_text="Hi"
        ),
        ExportMessage(
            message_id="msg2",
            message_type="message",
            time=1704067260,
            sender=sender2,
            elements=[MessageElement(type="text", data={"text": "Hello"})],
            raw_message="Hello",
            plain_text="Hello"
        )
    ]
    
    export_data = ExportData(metadata=metadata, messages=messages)
    assert export_data.metadata.chat_type == "private"
    assert len(export_data.messages) == 2
    assert export_data.messages[0].sender.nickname == "Alice"
    assert export_data.messages[1].sender.nickname == "Bob"
    print("✓ ExportData model works")


def test_json_serialization():
    """测试 JSON 序列化"""
    metadata = ExportMetadata(
        chat_type="group",
        chat_id="999",
        message_count=1
    )
    sender = SenderInfo(user_id="111", nickname="Test")
    message = ExportMessage(
        message_id="test",
        message_type="message",
        time=1704067200,
        sender=sender,
        elements=[MessageElement(type="text", data={"text": "Test"})],
        raw_message="Test",
        plain_text="Test"
    )
    export_data = ExportData(metadata=metadata, messages=[message])
    
    # 测试序列化
    json_data = export_data.model_dump(mode="json")
    assert json_data["metadata"]["chat_type"] == "group"
    assert json_data["messages"][0]["message_id"] == "test"
    print("✓ JSON serialization works")


if __name__ == "__main__":
    print("🚀 Running tests for nonebot-plugin-qq-chat-exporter\n")
    
    test_message_element()
    test_sender_info()
    test_export_message()
    test_export_metadata()
    test_export_data()
    test_json_serialization()
    
    print("\n✅ All 6 tests passed successfully!")
    print("\nThe core data models are working correctly.")
    print("The plugin is ready for integration with NoneBot2.")
