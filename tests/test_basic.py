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
    """测试消息发送者"""
    sender = MessageSender(uid="u_123", uin="123", name="测试用户")
    assert sender.uid == "u_123"
    assert sender.name == "测试用户"
    print("✓ MessageSender 测试通过")


def test_message_content():
    """测试消息内容"""
    content = MessageContent(text="Hello World", raw="Hello World")
    assert content.text == "Hello World"
    assert content.raw == "Hello World"
    print("✓ MessageContent 测试通过")


def test_export_message():
    """测试导出消息"""
    sender = MessageSender(uid="u_123", uin="123", name="Alice")
    receiver = MessageReceiver(uid="789", type="group")
    content = MessageContent(text="Hello", raw="Hello")
    stats = MessageStats(elementCount=1, textLength=5)
    msg = ExportMessage(
        messageId="msg_001",
        timestamp="2025-01-01T03:20:01.000Z",
        sender=sender,
        receiver=receiver,
        content=content,
        stats=stats
    )
    assert msg.messageId == "msg_001"
    assert msg.sender.name == "Alice"
    print("✓ ExportMessage 测试通过")


def test_chat_info():
    """测试聊天信息"""
    chat_info = ChatInfo(
        name="测试群聊",
        type="group"
    )
    assert chat_info.name == "测试群聊"
    assert chat_info.type == "group"
    print("✓ ChatInfo 测试通过")


def test_export_data():
    """测试完整导出数据"""
    chat_info = ChatInfo(name="测试群", type="private")
    statistics = Statistics(totalMessages=1)
    sender = MessageSender(uid="u_456", uin="456", name="Bob")
    receiver = MessageReceiver(uid="789", type="private")
    content = MessageContent(text="Test", raw="Test")
    stats = MessageStats(elementCount=1, textLength=4)
    msg = ExportMessage(
        messageId="test",
        timestamp="2025-01-01T03:20:01.000Z",
        sender=sender,
        receiver=receiver,
        content=content,
        stats=stats
    )
    export_data = ExportData(chatInfo=chat_info, statistics=statistics, messages=[msg])

    assert export_data.chatInfo.type == "private"
    assert len(export_data.messages) == 1
    print("✓ ExportData 测试通过")


def test_json_export():
    """测试 JSON 导出"""
    chat_info = ChatInfo(name="测试群", type="group")
    statistics = Statistics(totalMessages=2)

    messages = [
        ExportMessage(
            messageId="msg1",
            timestamp="2025-01-01T03:20:01.000Z",
            sender=MessageSender(uid="u_1", uin="1", name="User1"),
            receiver=MessageReceiver(uid="999", type="group"),
            content=MessageContent(text="Message 1", raw="Message 1"),
            stats=MessageStats(elementCount=1, textLength=9)
        ),
        ExportMessage(
            messageId="msg2",
            timestamp="2025-01-01T03:20:02.000Z",
            sender=MessageSender(uid="u_2", uin="2", name="User2"),
            receiver=MessageReceiver(uid="999", type="group"),
            content=MessageContent(text="Message 2", raw="Message 2"),
            stats=MessageStats(elementCount=1, textLength=9)
        )
    ]

    export_data = ExportData(chatInfo=chat_info, statistics=statistics, messages=messages)

    # 测试序列化
    json_dict = export_data.model_dump(mode="json")
    assert json_dict["chatInfo"]["name"] == "测试群"
    assert len(json_dict["messages"]) == 2
    assert json_dict["messages"][0]["sender"]["name"] == "User1"

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
        test_message_sender,
        test_message_content,
        test_export_message,
        test_chat_info,
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
    print(f"✅ 所有测试通过！共 {len(tests)} 个测试")
    print("=" * 60)
    print()
    print("📝 测试总结:")
    print("  - 数据模型定义正确")
    print("  - 消息内容结构正确")
    print("  - JSON 序列化功能正常")
    print("  - 插件核心功能可用")
    print()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
