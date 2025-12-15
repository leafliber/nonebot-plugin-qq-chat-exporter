"""
独立测试 - 测试核心功能而不依赖 NoneBot
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from nonebot_plugin_qq_chat_exporter.models import (
    ChatInfo,
    ExportData,
    ExportMessage,
    MessageContent,
    MessageReceiver,
    MessageSender,
    MessageStats,
    Statistics,
)


def test_message_sender():
    """测试消息发送者模型"""
    sender = MessageSender(
        uid="u_123456",
        uin="123456",
        name="测试用户"
    )
    assert sender.uid == "u_123456"
    assert sender.uin == "123456"
    assert sender.name == "测试用户"
    print("✓ MessageSender model works")


def test_message_receiver():
    """测试消息接收者模型"""
    receiver = MessageReceiver(
        uid="543612610",
        type="group"
    )
    assert receiver.uid == "543612610"
    assert receiver.type == "group"
    print("✓ MessageReceiver model works")


def test_message_content():
    """测试消息内容模型"""
    content = MessageContent(
        text="Hello World",
        raw="Hello World"
    )
    assert content.text == "Hello World"
    assert content.raw == "Hello World"
    print("✓ MessageContent model works")


def test_export_message():
    """测试导出消息模型"""
    sender = MessageSender(uid="u_123", uin="123", name="User")
    receiver = MessageReceiver(uid="789", type="group")
    content = MessageContent(text="测试消息", raw="测试消息")
    stats = MessageStats(elementCount=1, resourceCount=0, textLength=4)

    message = ExportMessage(
        messageId="msg_001",
        messageSeq="12345",
        timestamp="2025-01-01T03:20:01.000Z",
        sender=sender,
        receiver=receiver,
        content=content,
        stats=stats
    )
    assert message.messageId == "msg_001"
    assert message.sender.uid == "u_123"
    assert message.receiver.type == "group"
    assert message.content.text == "测试消息"
    print("✓ ExportMessage model works")


def test_chat_info():
    """测试聊天信息模型"""
    chat_info = ChatInfo(
        name="测试群聊",
        type="group"
    )
    assert chat_info.name == "测试群聊"
    assert chat_info.type == "group"
    print("✓ ChatInfo model works")


def test_export_data():
    """测试完整导出数据模型"""
    chat_info = ChatInfo(name="测试群", type="group")
    statistics = Statistics(totalMessages=2)

    sender1 = MessageSender(uid="u_123", uin="123", name="Alice")
    receiver1 = MessageReceiver(uid="789", type="group")
    content1 = MessageContent(text="Hi", raw="Hi")
    stats1 = MessageStats(elementCount=1, textLength=2)

    sender2 = MessageSender(uid="u_456", uin="456", name="Bob")
    receiver2 = MessageReceiver(uid="789", type="group")
    content2 = MessageContent(text="Hello", raw="Hello")
    stats2 = MessageStats(elementCount=1, textLength=5)

    messages = [
        ExportMessage(
            messageId="msg1",
            timestamp="2025-01-01T03:20:01.000Z",
            sender=sender1,
            receiver=receiver1,
            content=content1,
            stats=stats1
        ),
        ExportMessage(
            messageId="msg2",
            timestamp="2025-01-01T03:20:02.000Z",
            sender=sender2,
            receiver=receiver2,
            content=content2,
            stats=stats2
        )
    ]

    export_data = ExportData(
        chatInfo=chat_info,
        statistics=statistics,
        messages=messages
    )
    assert export_data.chatInfo.type == "group"
    assert len(export_data.messages) == 2
    assert export_data.messages[0].sender.name == "Alice"
    assert export_data.messages[1].sender.name == "Bob"
    print("✓ ExportData model works")


def test_json_serialization():
    """测试 JSON 序列化"""
    chat_info = ChatInfo(name="Test Group", type="group")
    statistics = Statistics(totalMessages=1)
    sender = MessageSender(uid="u_111", uin="111", name="Test")
    receiver = MessageReceiver(uid="999", type="group")
    content = MessageContent(text="Test", raw="Test")
    stats = MessageStats(elementCount=1, textLength=4)

    message = ExportMessage(
        messageId="test",
        timestamp="2025-01-01T03:20:01.000Z",
        sender=sender,
        receiver=receiver,
        content=content,
        stats=stats
    )
    export_data = ExportData(
        chatInfo=chat_info,
        statistics=statistics,
        messages=[message]
    )

    # 测试序列化
    json_data = export_data.model_dump(mode="json")
    assert json_data["chatInfo"]["type"] == "group"
    assert json_data["messages"][0]["messageId"] == "test"
    assert "metadata" in json_data
    assert "exportOptions" in json_data
    print("✓ JSON serialization works")


if __name__ == "__main__":
    print("🚀 Running tests for nonebot-plugin-qq-chat-exporter\n")

    test_message_sender()
    test_message_receiver()
    test_message_content()
    test_export_message()
    test_chat_info()
    test_export_data()
    test_json_serialization()

    print("\n✅ All 7 tests passed successfully!")
    print("\nThe core data models are working correctly.")
    print("The plugin is ready for integration with NoneBot2.")
