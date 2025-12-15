"""
测试消息转换功能
"""
from nonebot_plugin_qq_chat_exporter.converter import parse_message_content
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


def test_parse_text_message():
    """测试解析文本消息"""
    message_data = [
        {"type": "text", "data": {"text": "Hello World"}}
    ]
    content, text, resource_stats = parse_message_content(message_data)

    assert content.text == "Hello World"
    assert text == "Hello World"
    assert resource_stats["image"] == 0
    assert resource_stats["video"] == 0


def test_parse_mixed_message():
    """测试解析混合消息"""
    message_data = [
        {"type": "text", "data": {"text": "查看图片："}},
        {"type": "image", "data": {"url": "http://example.com/image.jpg"}},
        {"type": "text", "data": {"text": " 很好看"}}
    ]
    content, text, resource_stats = parse_message_content(message_data)

    assert text == "查看图片：[图片] 很好看"
    assert resource_stats["image"] == 1
    assert len(content.resources) == 1


def test_parse_at_message():
    """测试解析@消息"""
    message_data = [
        {"type": "at", "data": {"qq": "123456"}},
        {"type": "text", "data": {"text": " 你好"}}
    ]
    content, text, resource_stats = parse_message_content(message_data)

    assert text == "@123456 你好"


def test_export_message_model():
    """测试导出消息模型"""
    sender = MessageSender(
        uid="u_123456",
        uin="123456",
        name="测试用户"
    )
    receiver = MessageReceiver(
        uid="789012",
        type="group"
    )
    content = MessageContent(text="测试消息", raw="测试消息")
    stats = MessageStats(elementCount=1)

    message = ExportMessage(
        messageId="msg_001",
        timestamp="2025-01-01T03:20:01.000Z",
        sender=sender,
        receiver=receiver,
        content=content,
        stats=stats
    )

    assert message.messageId == "msg_001"
    assert message.sender.uid == "u_123456"
    assert message.receiver.type == "group"


def test_export_data_model():
    """测试完整导出数据模型"""
    chat_info = ChatInfo(
        name="测试群",
        type="group"
    )
    statistics = Statistics(totalMessages=1)

    sender = MessageSender(uid="u_123456", uin="123456", name="用户1")
    receiver = MessageReceiver(uid="789012", type="group")
    content = MessageContent(text="测试", raw="测试")
    stats = MessageStats(elementCount=1, textLength=2)

    message = ExportMessage(
        messageId="msg_001",
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

    assert export_data.chatInfo.type == "group"
    assert export_data.statistics.totalMessages == 1
    assert len(export_data.messages) == 1
    assert export_data.messages[0].messageId == "msg_001"


if __name__ == "__main__":
    # 运行测试
    test_parse_text_message()
    print("✓ test_parse_text_message passed")

    test_parse_mixed_message()
    print("✓ test_parse_mixed_message passed")

    test_parse_at_message()
    print("✓ test_parse_at_message passed")

    test_export_message_model()
    print("✓ test_export_message_model passed")

    test_export_data_model()
    print("✓ test_export_data_model passed")

    print("\n✅ All tests passed!")
