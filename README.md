# nonebot-plugin-qq-chat-exporter

兼容 [qq-chat-exporter](https://github.com/shuakami/qq-chat-exporter) 格式的 QQ 消息导出插件

## 简介

这是一个 NoneBot2 插件，可以导出指定群聊或私聊的聊天消息，导出格式兼容 qq-chat-exporter 项目的 JSON 格式。

本插件使用 [nonebot-plugin-chatrecorder](https://github.com/noneplugin/nonebot-plugin-chatrecorder) 的 API 来获取聊天记录，并提供了 WebUI 界面来方便地进行导出操作。

## 功能特性

- ✅ 导出群聊消息
- ✅ 导出私聊消息
- ✅ 支持指定时间范围导出
- ✅ 兼容 qq-chat-exporter 的 JSON 格式
- ✅ 提供 WebUI 进行可视化操作
- ✅ 提供 RESTful API 接口

## 安装

### 使用 pip

```bash
pip install nonebot-plugin-qq-chat-exporter
```

### 使用 poetry

```bash
poetry add nonebot-plugin-qq-chat-exporter
```

### 使用 nb-cli

```bash
nb plugin install nonebot-plugin-qq-chat-exporter
```

## 配置

在 NoneBot2 项目的配置文件中加载插件：

```python
# bot.py
import nonebot

nonebot.init()

# 加载插件
nonebot.load_plugin("nonebot_plugin_chatrecorder")  # 必须先加载
nonebot.load_plugin("nonebot_plugin_qq_chat_exporter")

if __name__ == "__main__":
    nonebot.run()
```

## 使用方法

### WebUI 界面

启动机器人后，访问以下地址：

```
http://localhost:8080/qq-chat-exporter
```

（端口根据你的 NoneBot 配置可能有所不同）

在 WebUI 界面中：

1. 选择聊天类型（群聊/私聊）
2. 输入群号或 QQ 号
3. 可选：设置开始和结束时间
4. 点击"开始导出"按钮

导出的 JSON 文件将保存在 `exports/` 目录下。

### API 接口

#### 导出消息

**接口地址：** `POST /qq-chat-exporter/export`

**请求参数：**

```json
{
  "chat_type": "group",           // "group" 或 "private"
  "chat_id": "123456789",         // 群号或 QQ 号
  "start_time": "2024-01-01T00:00:00Z",  // 可选，开始时间（ISO 8601 格式）
  "end_time": "2024-12-31T23:59:59Z",    // 可选，结束时间（ISO 8601 格式）
  "output_dir": "exports"         // 可选，输出目录
}
```

**响应示例：**

```json
{
  "success": true,
  "message": "导出成功",
  "file_path": "exports/group_123456789_20241215_120000.json"
}
```

#### 健康检查

**接口地址：** `GET /qq-chat-exporter/health`

**响应示例：**

```json
{
  "status": "ok"
}
```

### Python API

你也可以在代码中直接调用导出函数：

```python
from datetime import datetime
from nonebot_plugin_qq_chat_exporter import export_group_messages, export_private_messages

# 导出群聊消息
file_path = await export_group_messages(
    group_id="123456789",
    start_time=datetime(2024, 1, 1),
    end_time=datetime(2024, 12, 31),
    output_dir="exports"
)

# 导出私聊消息
file_path = await export_private_messages(
    user_id="987654321",
    start_time=datetime(2024, 1, 1),
    end_time=datetime(2024, 12, 31),
    output_dir="exports"
)
```

## 导出格式

导出的 JSON 文件格式兼容 qq-chat-exporter，包含以下结构：

```json
{
  "metadata": {
    "export_time": "2024-12-15T12:00:00",
    "exporter": "nonebot-plugin-qq-chat-exporter",
    "version": "0.1.0",
    "chat_type": "group",
    "chat_id": "123456789",
    "chat_name": "Group 123456789",
    "message_count": 100,
    "time_range": {
      "start": 1704067200,
      "end": 1735689599
    }
  },
  "messages": [
    {
      "message_id": "msg123",
      "message_type": "message",
      "time": 1704067200,
      "sender": {
        "user_id": "123456",
        "nickname": "用户昵称",
        "card": "",
        "role": "member"
      },
      "elements": [
        {
          "type": "text",
          "data": {
            "text": "消息内容"
          }
        }
      ],
      "raw_message": "消息内容",
      "plain_text": "消息内容"
    }
  ]
}
```

## 依赖项

- nonebot2 >= 2.3.0
- nonebot-plugin-chatrecorder >= 0.7.0
- nonebot-plugin-htmlrender >= 0.3.0

## 许可证

本项目使用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关项目

- [nonebot-plugin-chatrecorder](https://github.com/noneplugin/nonebot-plugin-chatrecorder) - NoneBot2 聊天记录插件
- [qq-chat-exporter](https://github.com/shuakami/qq-chat-exporter) - QQ 聊天记录导出工具

