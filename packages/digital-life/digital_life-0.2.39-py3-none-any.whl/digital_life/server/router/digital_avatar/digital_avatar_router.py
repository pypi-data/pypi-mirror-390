
from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, status
import inspect
from digital_life import logger
# server
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, model_validator, field_validator, RootModel
from digital_life.model_public import MemoryCard
from .digital_avatar import DigitalAvatar

router = APIRouter(tags=["digital_avatar"])
da = DigitalAvatar(inference_save_case = False,
                   model_name = "doubao-1-5-pro-32k-250115")


class BriefResponse(BaseModel):
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    tags: list[str] = Field(..., description='["标签1","标签2"]')


class MemoryCards(BaseModel):
    memory_cards: list[MemoryCard] = Field(..., description="记忆卡片列表")


@router.post(
    "/brief", response_model=BriefResponse, description="数字分身介绍"
)
async def brief_server(request: MemoryCards):
    try:
        memory_cards = request.model_dump()["memory_cards"]
        result = await da.abrief(memory_cards=memory_cards)
        return BriefResponse(
        title=result.get("title"),
        content=result.get("content"),
        tags=result.get("tags")[:2],)
    except Exception as e:
        frame = inspect.currentframe()
        info = inspect.getframeinfo(frame)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Function name: {info.function} : {e}",
        )

class AvatarXGRequests(BaseModel):
    action: str
    old_character: str
    memory_cards: list[MemoryCard]
    

@router.post("/personality_extraction")
async def digital_avatar_personality_extraction(request: AvatarXGRequests):
    """数字分身性格提取"""
    try:
        memory_cards = request.model_dump()["memory_cards"]
        result = await da.personality_extraction(memory_cards=memory_cards,action = request.action,old_character = request.old_character)
        return {"text": result}
    except Exception as e:
        frame = inspect.currentframe()
        info = inspect.getframeinfo(frame)
        logger.error(f'{e} & {type(memory_cards)} & {memory_cards}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Function name: {info.function} : {e}",
        )


@router.post("/desensitization",response_model=MemoryCards)
async def digital_avatar_desensitization(request: MemoryCards):
    """
    数字分身脱敏
    """
    try:
        input_ = request.model_dump()["memory_cards"]
        result = await da.desensitization(memory_cards=input_)
        memory_cards = {"memory_cards": result}
        return MemoryCards(**memory_cards)
    except Exception as e:
        frame = inspect.currentframe()
        info = inspect.getframeinfo(frame)
        logger.error(f'{e} & {type(input_)} & {input_}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Function name: {info.function} : {e}",
        )