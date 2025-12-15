"""
WebUI 路由和API
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

from nonebot import get_driver, require
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

require("nonebot_plugin_chatrecorder")

from .exporter import export_group_messages, export_private_messages


class ExportRequest(BaseModel):
    """导出请求"""
    chat_type: str  # "group" or "private"
    chat_id: str
    start_time: Optional[str] = None  # ISO format datetime string
    end_time: Optional[str] = None  # ISO format datetime string
    output_dir: Optional[str] = None


class ExportResponse(BaseModel):
    """导出响应"""
    success: bool
    message: str
    file_path: Optional[str] = None


# 获取 FastAPI 应用实例
driver = get_driver()
app: FastAPI = driver.server_app


@app.get("/qq-chat-exporter", response_class=HTMLResponse)
async def index():
    """WebUI 首页"""
    template_path = Path(__file__).parent / "templates" / "index.html"
    with open(template_path, encoding="utf-8") as f:
        return f.read()


@app.post("/qq-chat-exporter/export", response_model=ExportResponse)
async def export_messages(request: ExportRequest):
    """
    导出消息接口

    Args:
        request: 导出请求

    Returns:
        导出响应
    """
    try:
        # 解析时间
        start_time = None
        end_time = None

        if request.start_time:
            try:
                start_time = datetime.fromisoformat(request.start_time.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_time format")

        if request.end_time:
            try:
                end_time = datetime.fromisoformat(request.end_time.replace("Z", "+00:00"))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_time format")

        # 根据聊天类型调用相应的导出函数
        if request.chat_type == "group":
            file_path = await export_group_messages(
                group_id=request.chat_id,
                start_time=start_time,
                end_time=end_time,
                output_dir=request.output_dir
            )
        elif request.chat_type == "private":
            file_path = await export_private_messages(
                user_id=request.chat_id,
                start_time=start_time,
                end_time=end_time,
                output_dir=request.output_dir
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid chat_type")

        return ExportResponse(
            success=True,
            message="导出成功",
            file_path=file_path
        )

    except Exception as e:
        return ExportResponse(
            success=False,
            message=f"导出失败: {str(e)}"
        )


@app.get("/qq-chat-exporter/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}
