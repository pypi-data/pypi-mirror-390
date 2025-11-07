from fastapi import HTTPException, status, APIRouter
import inspect
from digital_life import logger
# server
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from digital_life.model_public import MemoryCard
from .user import UserInfo

router = APIRouter(tags=["user"])

userinfo = UserInfo(inference_save_case = False,model_name = "doubao-1-5-pro-256k-250115")


class UseroverviewRequests(BaseModel):
    action: str
    old_overview: str
    memory_cards: list[MemoryCard]

@router.post("/user_overview")
async def user_overview_server(request: UseroverviewRequests):
    """
    用户概述
    """
    try:
        memory_cards = request.model_dump()["memory_cards"]
        result = await userinfo.auser_overview(
            action = request.action,
            old_overview=request.old_overview, 
            memory_cards=memory_cards
        )  # 包裹的内核函数

        return {"overview": result}
    except Exception as e:
        frame = inspect.currentframe()
        info = inspect.getframeinfo(frame)
        logger.error(f'{e} $ {info.function} $  -')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Function name: {info.function} : {e}",
        )


class UserRelationshipExtractionRequest(BaseModel):
    text: str

@router.post("/user_relationship_extraction", description="用户关系提取")
async def user_relationship_extraction_server(request: UserRelationshipExtractionRequest,):
    try:
        result = await userinfo.auser_relationship_extraction(text=request.text)
        return {"relation": result}
    except Exception as e:
        frame = inspect.currentframe()
        info = inspect.getframeinfo(frame)

        logger.error(f'{e} $ {info.function} $  -')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Function name: {info.function} : {e}",
        )
