
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from digital_life.models import BiographyRequest, BiographyResult
from digital_life import logger
import asyncio
import httpx
import inspect
import uuid
from digital_life.redis_ import get_value
from .biography2 import BiographyGenerate

bg = BiographyGenerate(inference_save_case = True,
                       model_name = "doubao-1-5-pro-256k-250115")

router = APIRouter(tags=["biography"])

# 免费版传记优化
@router.post("/generate_biography_free", summary="提交传记生成请求")
async def generate_biography(request: BiographyRequest):
    """
    提交一个传记生成请求。

    此接口会立即返回一个任务ID，客户端可以使用此ID查询生成进度和结果。
    实际的生成过程会在后台异步执行。
    """
    try:
        memory_cards = request.model_dump()["memory_cards"]
        result = await bg.agenerate_biography_free(
            user_name=request.user_name,
            memory_cards=memory_cards,
            vitae=request.vitae,
        )
        return result
    except Exception as e:
        frame = inspect.currentframe()
        info = inspect.getframeinfo(frame)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Function name: {info.function} : {e}",
        )


@router.post(
    "/generate_biography", response_model=BiographyResult, summary="提交传记生成请求"
)
async def generate_biography(request: BiographyRequest):
    """
    提交一个传记生成请求。

    此接口会立即返回一个任务ID，客户端可以使用此ID查询生成进度和结果。
    实际的生成过程会在后台异步执行。
    """
    try:

        task_id = str(uuid.uuid4())
        memory_cards = request.model_dump()["memory_cards"]
        vitae = request.vitae
        user_name = request.user_name
        print(1234)
        asyncio.create_task(bg._generate_biography(task_id, 
                                                   memory_cards = memory_cards,
                                                   vitae = vitae,
                                                   user_name = user_name
                                                   ))
        return BiographyResult(task_id=task_id, status="PENDING", progress=0.0)

    except Exception as e:
        frame = inspect.currentframe()
        info = inspect.getframeinfo(frame)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Function name: {info.function} : {e}",
        )

@router.get(
    "/get_biography_result/{task_id}",
    response_model=BiographyResult,
    summary="查询传记生成结果",
)
async def get_biography_result(task_id: str):
    """
    根据任务ID查询传记生成任务的状态和结果。
    """
    try:
        task_info = get_value(bg.biograph_redis,task_id)
        if not task_info:
            raise HTTPException(
                status_code=404, detail=f"Task with ID '{task_id}' not found."
            )
        return BiographyResult(
            task_id=task_info["task_id"],
            status=task_info["status"],
            biography_title=task_info.get("biography_title", "未知"),
            biography_brief=task_info.get("biography_brief", "未知"),
            biography_json=task_info.get("biography_json", {}),
            biography_name=task_info.get("biography_name", []),
            biography_place=task_info.get("biography_place", []),
            error_message=task_info.get("error_message"),
            progress=task_info.get("progress", 0.0),
        )
            
    except Exception as e:
        frame = inspect.currentframe()
        info = inspect.getframeinfo(frame)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Function name: {info.function} : {e}",
        )



