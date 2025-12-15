"""
测试消息转换功能
"""
from datetime import datetime

from nonebot_plugin_qq_chat_exporter.converter import parse_message_elements
from nonebot_plugin_qq_chat_exporter.models import (
    ExportData,
    ExportMessage,
    ExportMetadata,
    MessageElement,
    SenderInfo,
)


def test_parse_text_message():
    """测试解析文本消息"""
    message_data = [
        {"type": "text", "data": {"text": "Hello World"}}
    ]
    elements, raw_message = parse_message_elements(message_data)
    
    assert len(elements) == 1
    assert elements[0].type == "text"
    assert elements[0].data["text"] == "Hello World"
    assert raw_message == "Hello World"


def test_parse_mixed_message():
    """测试解析混合消息"""
    message_data = [
        {"type": "text", "data": {"text": "查看图片："}},
        {"type": "image", "data": {"url": "http://example.com/image.jpg"}},
        {"type": "text", "data": {"text": " 很好看"}}
    ]
    elements, raw_message = parse_message_elements(message_data)
    
    assert len(elements) == 3
    assert elements[0].type == "text"
    assert elements[1].type == "image"
    assert elements[2].type == "text"
    assert raw_message == "查看图片：[图片] 很好看"


def test_parse_at_message():
    """测试解析@消息"""
    message_data = [
        {"type": "at", "data": {"qq": "123456"}},
        {"type": "text", "data": {"text": " 你好"}}
    ]
    elements, raw_message = parse_message_elements(message_data)
    
    assert len(elements) == 2
    assert elements[0].type == "at"
    assert raw_message == "@123456 你好"


def test_export_message_model():
    """测试导出消息模型"""
    sender = SenderInfo(
        user_id="123456",
        nickname="测试用户",
        card="",
        role="member"
    )
    
    message = ExportMessage(
        message_id="msg_001",
        message_type="message",
        time=int(datetime.now().timestamp()),
        sender=sender,
        elements=[
            MessageElement(type="text", data={"text": "测试消息"})
        ],
        raw_message="测试消息",
        plain_text="测试消息"
    )
    
    assert message.message_id == "msg_001"
    assert message.sender.user_id == "123456"
    assert len(message.elements) == 1


def test_export_data_model():
    """测试完整导出数据模型"""
    metadata = ExportMetadata(
        export_time=datetime.now(),
        chat_type="group",
        chat_id="789012",
        chat_name="测试群",
        message_count=1,
        time_range={"start": 1704067200, "end": 1704153600}
    )
    
    sender = SenderInfo(user_id="123456", nickname="用户1")
    message = ExportMessage(
        message_id="msg_001",
        message_type="message",
        time=1704067200,
        sender=sender,
        elements=[MessageElement(type="text", data={"text": "测试"})],
        raw_message="测试",
        plain_text="测试"
    )
    
    export_data = ExportData(
        metadata=metadata,
        messages=[message]
    )
    
    assert export_data.metadata.chat_type == "group"
    assert export_data.metadata.message_count == 1
    assert len(export_data.messages) == 1
    assert export_data.messages[0].message_id == "msg_001"


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
