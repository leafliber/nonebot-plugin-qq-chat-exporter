# nonebot-plugin-qq-chat-exporter

兼容qq-chat-exporter格式的QQ消息导出插件

## 简介

这是一个 NoneBot2 插件，用于导出 QQ 聊天记录，并兼容 [qq-chat-exporter](https://github.com/shuakami/qq-chat-exporter) 项目的 JSON 格式。

## 安装

使用 pip 安装：

```bash
pip install nonebot-plugin-qq-chat-exporter
```

或者从源码安装：

```bash
git clone https://github.com/leafliber/nonebot-plugin-qq-chat-exporter.git
cd nonebot-plugin-qq-chat-exporter
pip install -e .
```

## 配置

在 NoneBot2 的 `.env` 文件中添加以下配置项（可选）：

```env
# 导出文件保存目录，默认为 ./exports
QQ_CHAT_EXPORTER_OUTPUT_DIR=./exports

# 是否包含系统消息，默认为 true
QQ_CHAT_EXPORTER_INCLUDE_SYSTEM=true

# 是否包含资源链接，默认为 true
QQ_CHAT_EXPORTER_INCLUDE_RESOURCES=true

# 时间格式，默认为 YYYY-MM-DD HH:mm:ss
QQ_CHAT_EXPORTER_TIME_FORMAT=YYYY-MM-DD HH:mm:ss

# 文件编码，默认为 utf-8
QQ_CHAT_EXPORTER_ENCODING=utf-8
```

## 使用方法

### 基本命令

1. **开始导出**: 在群聊或私聊中发送 `/export` 或 `导出` 命令
2. **完成导出**: 发送 `/export_finish` 或 `完成导出` 命令

### 使用示例

```
用户: /export
Bot: 开始导出消息，请继续发送消息或使用 /export_finish 完成导出

[... 继续聊天 ...]

用户: /export_finish
Bot: 导出完成！
     共导出 100 条消息
     文件保存在: ./exports/export_group_123456_20250115_134800.json
```

## 导出格式

导出的 JSON 文件完全兼容 qq-chat-exporter 格式，包含以下结构：

```json
{
  "metadata": {
    "name": "exporter",
    "copyright": "",
    "version": "4.0.0"
  },
  "chatInfo": {
    "name": "聊天名称",
    "type": "group"
  },
  "statistics": {
    "totalMessages": 100,
    "timeRange": {
      "start": "2025-01-01T00:00:00.000Z",
      "end": "2025-01-15T13:48:00.000Z",
      "durationDays": 0
    },
    "messageTypes": {
      "unknown": 100
    },
    "senders": [
      {
        "uid": "123456",
        "name": "用户名",
        "messageCount": 50,
        "percentage": 50.0
      }
    ],
    "resources": {
      "total": 10,
      "byType": {
        "image": 8,
        "video": 1,
        "audio": 1,
        "file": 0
      },
      "totalSize": 0
    }
  },
  "messages": [
    {
      "messageId": "123",
      "messageSeq": "1",
      "msgRandom": "0",
      "timestamp": "2025-01-01T00:00:00.000Z",
      "sender": {
        "uid": "123456",
        "uin": "123456",
        "name": "用户名"
      },
      "receiver": {
        "uid": "654321",
        "type": "group"
      },
      "messageType": 0,
      "isSystemMessage": false,
      "isRecalled": false,
      "isTempMessage": false,
      "content": {
        "text": "消息内容",
        "html": "",
        "raw": "消息内容",
        "mentions": [],
        "resources": [],
        "emojis": [],
        "special": []
      },
      "stats": {
        "elementCount": 1,
        "resourceCount": 0,
        "textLength": 4,
        "processingTime": 0
      },
      "rawMessage": null
    }
  ],
  "exportOptions": {
    "includedFields": ["id", "timestamp", "sender", "content", "resources"],
    "filters": {},
    "options": {
      "includeResourceLinks": true,
      "includeSystemMessages": true,
      "timeFormat": "YYYY-MM-DD HH:mm:ss",
      "encoding": "utf-8"
    }
  }
}
```

## 开发

### 项目结构

```
nonebot_plugin_qq_chat_exporter/
├── __init__.py      # 插件主文件
├── config.py        # 配置定义
├── exporter.py      # 导出功能实现
└── models.py        # 数据模型定义
```

### API 使用

插件也可以作为库使用：

```python
from nonebot_plugin_qq_chat_exporter import ChatExporter

# 创建导出器
exporter = ChatExporter()
exporter.set_chat_info("我的群聊", "group")

# 添加消息
exporter.add_message(
    message_id="123",
    message_seq="1",
    timestamp="2025-01-01T00:00:00.000Z",
    sender_uid="123456",
    sender_name="用户名",
    receiver_uid="654321",
    receiver_type="group",
    content_text="Hello, World!"
)

# 导出
export_data = exporter.export("./output.json")
```

## 许可证

MIT License

## 相关项目

- [qq-chat-exporter](https://github.com/shuakami/qq-chat-exporter) - QQ聊天记录导出工具
- [NoneBot2](https://github.com/nonebot/nonebot2) - 跨平台 Python 异步聊天机器人框架
