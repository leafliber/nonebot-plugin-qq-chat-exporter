"""
WebUI 路由和API
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from nonebot import get_driver, require, get_bot
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel

require("nonebot_plugin_chatrecorder")

from .exporter import export_group_messages, export_private_messages

logger = logging.getLogger(__name__)


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


@app.get("/qq-chat-exporter/groups")
async def get_groups():
    """获取群列表"""
    try:
        bot = get_bot()
        if hasattr(bot, "get_group_list"):
            groups = await bot.get_group_list()
            return {
                "success": True,
                "data": [
                    {"id": str(g["group_id"]), "name": g["group_name"]}
                    for g in groups
                ]
            }
    except Exception as e:
        logger.warning(f"Failed to get group list: {e}")
    
    return {"success": False, "message": "Failed to get group list", "data": []}


@app.get("/qq-chat-exporter", response_class=HTMLResponse)
async def index():
    """WebUI 首页"""
    try:
        template_path = Path(__file__).parent / "templates" / "index.html"
        # 确保路径在预期目录内
        if not template_path.is_file():
            raise HTTPException(status_code=500, detail="Template file not found")
        with open(template_path, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load template: {str(e)}")


@app.post("/qq-chat-exporter/export")
async def export_messages(request: ExportRequest):
    """
    导出消息接口

    Args:
        request: 导出请求

    Returns:
        导出响应
    """
    try:
        logger.info(f"Received export request for {request.chat_type} {request.chat_id}")
        
        # 解析时间
        start_time = None
        end_time = None

        if request.start_time:
            try:
                start_time = datetime.fromisoformat(request.start_time.replace("Z", "+00:00"))
            except ValueError as e:
                logger.warning(f"Invalid start_time format: {request.start_time}")
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "message": f"Invalid start_time format: {str(e)}"
                    }
                )

        if request.end_time:
            try:
                end_time = datetime.fromisoformat(request.end_time.replace("Z", "+00:00"))
            except ValueError as e:
                logger.warning(f"Invalid end_time format: {request.end_time}")
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "message": f"Invalid end_time format: {str(e)}"
                    }
                )

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
            logger.warning(f"Invalid chat_type: {request.chat_type}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Invalid chat_type. Must be 'group' or 'private'"
                }
            )

        logger.info(f"Export completed successfully: {file_path}")
        return JSONResponse(
            content={
                "success": True,
                "message": "导出成功",
                "file_path": file_path
            }
        )

    except Exception as e:
        # 确保即使发生异常也返回JSON格式
        logger.error(f"Export failed: {type(e).__name__} - {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"导出失败: {type(e).__name__} - {str(e)}"
            }
        )


@app.get("/qq-chat-exporter/download")
async def download_file(file_path: str = Query(..., description="File path to download")):
    """下载文件接口"""
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=path,
        filename=path.name,
        media_type="application/octet-stream"
    )


@app.get("/qq-chat-exporter/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}
