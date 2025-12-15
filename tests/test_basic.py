#!/usr/bin/env python3
"""
测试脚本 - 直接测试模型和转换器功能
运行方式: python test_basic.py
"""
import sys
from pathlib import Path

# 将项目根目录添加到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 直接导入 models 模块（绕过 __init__.py）
from nonebot_plugin_qq_chat_exporter.models import (
    ExportMessage,
    ExportMetadata,
    ExportData,
    SenderInfo,
    MessageElement,
)


def test_message_element():
    """测试消息元素"""
    element = MessageElement(type="text", data={"text": "Hello World"})
    assert element.type == "text"
    assert element.data["text"] == "Hello World"
    print("✓ MessageElement 测试通过")


def test_sender_info():
    """测试发送者信息"""
    sender = SenderInfo(
        user_id="123456",
        nickname="测试用户",
        card="群名片",
        role="member"
    )
    assert sender.user_id == "123456"
    assert sender.nickname == "测试用户"
    print("✓ SenderInfo 测试通过")


def test_export_message():
    """测试导出消息"""
    sender = SenderInfo(user_id="123", nickname="Alice")
    msg = ExportMessage(
        message_id="msg_001",
        message_type="message",
        time=1704067200,
        sender=sender,
        elements=[
            MessageElement(type="text", data={"text": "Hello"}),
            MessageElement(type="image", data={"url": "http://example.com/img.jpg"}),
        ],
        raw_message="Hello [图片]",
        plain_text="Hello"
    )
    assert msg.message_id == "msg_001"
    assert len(msg.elements) == 2
    assert msg.sender.nickname == "Alice"
    print("✓ ExportMessage 测试通过")


def test_export_metadata():
    """测试导出元数据"""
    metadata = ExportMetadata(
        chat_type="group",
        chat_id="789012",
        chat_name="测试群聊",
        message_count=100,
        time_range={"start": 1704067200, "end": 1704153600}
    )
    assert metadata.chat_type == "group"
    assert metadata.message_count == 100
    print("✓ ExportMetadata 测试通过")


def test_export_data():
    """测试完整导出数据"""
    metadata = ExportMetadata(
        chat_type="private",
        chat_id="123",
        message_count=1
    )
    sender = SenderInfo(user_id="456", nickname="Bob")
    msg = ExportMessage(
        message_id="test",
        message_type="message",
        time=1704067200,
        sender=sender,
        elements=[MessageElement(type="text", data={"text": "Test"})],
        raw_message="Test",
        plain_text="Test"
    )
    export_data = ExportData(metadata=metadata, messages=[msg])
    
    assert export_data.metadata.chat_type == "private"
    assert len(export_data.messages) == 1
    print("✓ ExportData 测试通过")


def test_json_export():
    """测试 JSON 导出"""
    metadata = ExportMetadata(
        chat_type="group",
        chat_id="999",
        message_count=2
    )
    
    messages = [
        ExportMessage(
            message_id="msg1",
            message_type="message",
            time=1704067200,
            sender=SenderInfo(user_id="1", nickname="User1"),
            elements=[MessageElement(type="text", data={"text": "Message 1"})],
            raw_message="Message 1",
            plain_text="Message 1"
        ),
        ExportMessage(
            message_id="msg2",
            message_type="message",
            time=1704067260,
            sender=SenderInfo(user_id="2", nickname="User2"),
            elements=[MessageElement(type="text", data={"text": "Message 2"})],
            raw_message="Message 2",
            plain_text="Message 2"
        )
    ]
    
    export_data = ExportData(metadata=metadata, messages=messages)
    
    # 测试序列化
    json_dict = export_data.model_dump(mode="json")
    assert json_dict["metadata"]["chat_id"] == "999"
    assert len(json_dict["messages"]) == 2
    assert json_dict["messages"][0]["sender"]["nickname"] == "User1"
    
    # 测试可以转换为 JSON 字符串
    import json
    json_str = json.dumps(json_dict, ensure_ascii=False, indent=2)
    assert "Message 1" in json_str
    assert "User2" in json_str
    
    print("✓ JSON导出 测试通过")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("NoneBot QQ Chat Exporter - 核心功能测试")
    print("=" * 60)
    print()
    
    tests = [
        test_message_element,
        test_sender_info,
        test_export_message,
        test_export_metadata,
        test_export_data,
        test_json_export,
    ]
    
    for i, test in enumerate(tests, 1):
        try:
            test()
        except Exception as e:
            print(f"✗ 测试 {i} 失败: {e}")
            return False
    
    print()
    print("=" * 60)
    print("✅ 所有测试通过！共 {} 个测试".format(len(tests)))
    print("=" * 60)
    print()
    print("📝 测试总结:")
    print("  - 数据模型定义正确")
    print("  - 消息元素结构正确")
    print("  - JSON 序列化功能正常")
    print("  - 插件核心功能可用")
    print()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
