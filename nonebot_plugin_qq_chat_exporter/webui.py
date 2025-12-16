"""
WebUI 路由和API
"""
import asyncio
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from nonebot import get_driver, require, get_bot
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel

require("nonebot_plugin_chatrecorder")

from .exporter import export_group_messages, export_private_messages

logger = logging.getLogger(__name__)

# 任务存储
# task_id -> {status: str, message: str, file_path: str, created_at: datetime}
export_tasks: Dict[str, Dict[str, Any]] = {}

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


async def _run_export_task(task_id: str, request: ExportRequest):
    """后台执行导出任务"""
    try:
        logger.info(f"Starting export task {task_id} for {request.chat_type} {request.chat_id}")
        export_tasks[task_id]["status"] = "processing"
        
        # 解析时间
        start_time = None
        end_time = None

        if request.start_time:
            start_time = datetime.fromisoformat(request.start_time.replace("Z", "+00:00"))

        if request.end_time:
            end_time = datetime.fromisoformat(request.end_time.replace("Z", "+00:00"))

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
            raise ValueError(f"Invalid chat_type: {request.chat_type}")

        export_tasks[task_id]["status"] = "completed"
        export_tasks[task_id]["file_path"] = file_path
        export_tasks[task_id]["message"] = "导出成功"
        logger.info(f"Task {task_id} completed successfully: {file_path}")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {type(e).__name__} - {str(e)}", exc_info=True)
        export_tasks[task_id]["status"] = "failed"
        export_tasks[task_id]["message"] = f"导出失败: {type(e).__name__} - {str(e)}"


@app.post("/qq-chat-exporter/export")
async def export_messages(request: ExportRequest, background_tasks: BackgroundTasks):
    """
    导出消息接口 (异步任务)
    """
    try:
        # 验证时间格式
        if request.start_time:
            try:
                datetime.fromisoformat(request.start_time.replace("Z", "+00:00"))
            except ValueError as e:
                return JSONResponse(status_code=400, content={"success": False, "message": f"Invalid start_time: {e}"})
        
        if request.end_time:
            try:
                datetime.fromisoformat(request.end_time.replace("Z", "+00:00"))
            except ValueError as e:
                return JSONResponse(status_code=400, content={"success": False, "message": f"Invalid end_time: {e}"})

        # 创建任务
        task_id = str(uuid.uuid4())
        export_tasks[task_id] = {
            "status": "pending",
            "message": "任务已创建",
            "created_at": datetime.now(),
            "file_path": None
        }
        
        # 添加后台任务
        background_tasks.add_task(_run_export_task, task_id, request)
        
        return JSONResponse(
            content={
                "success": True,
                "message": "导出任务已开始",
                "task_id": task_id
            }
        )

    except Exception as e:
        logger.error(f"Failed to create export task: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"创建任务失败: {str(e)}"
            }
        )


@app.get("/qq-chat-exporter/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    task = export_tasks.get(task_id)
    if not task:
        return JSONResponse(status_code=404, content={"success": False, "message": "Task not found"})
    
    return JSONResponse(content={
        "success": True,
        "status": task["status"],
        "message": task["message"],
        "file_path": task.get("file_path")
    })


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
