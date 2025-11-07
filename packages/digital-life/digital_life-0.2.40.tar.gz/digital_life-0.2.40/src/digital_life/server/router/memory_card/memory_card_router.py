from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, status
import os
from pydantic import BaseModel, Field, model_validator, field_validator, RootModel
import re
import inspect
from digital_life import logger
from digital_life.model_public import MemoryCard
from .memorycard import MemoryCardManager

router = APIRouter(tags=["memory_card"])

MCmanager = MemoryCardManager(model_name="doubao-1-5-pro-32k-250115",
                              inference_save_case=True)


# doubao-1-5-pro-32k-250115
# doubao-seed-1-6-lite-251015





# 每一个都要有models 控制输入输出
# 每一个都要欧description, response_description


class MemoryCardScoreRequest(BaseModel):
    memory_cards: list[str] = Field(..., description="记忆卡片列表")

@router.post("/score",response_model = None, description="记忆卡片质量评分")
async def score_from_memory_card_server(request: MemoryCardScoreRequest):
    try:
        input_ = {"memory_cards":request.memory_cards}
        results = await MCmanager.ascore_from_memory_card(**input_)
        return {"message": "memory card score successfully", "result": results}
    except Exception as e:
        logger.error(f'{e} & {type(input_)} & {input_}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error Info: {e}",
        )

class MemoryCards(BaseModel):
    memory_cards: list[MemoryCard] = Field(..., description="记忆卡片列表")
    brithday: str = None
    age: str = None

@router.post("/merge", response_model=MemoryCard, description="记忆卡片合并")
async def memory_card_merge_server(request: MemoryCards) -> dict:
    try:
        # input_ = {"memory_cards":request.model_dump()["memory_cards"]}
        input_ = str(request.memory_cards)
        result = await MCmanager.amemory_card_merge(memory_cards=input_,
                                                    brithday= request.brithday, 
                                                    age = request.age)
        
        return MemoryCard(**result)

    except Exception as e:
        logger.error(f'{e} & {type(input_)} & {input_}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error Info: {e}",
        )




@router.post("/polish", response_model=MemoryCard, description="记忆卡片发布AI润色")
async def memory_card_polish_server(request: MemoryCard) -> dict:
    """
    记忆卡片发布AI润色接口。
    接收记忆卡片内容，并返回AI润色后的结果。
    """
    try:
        input_ = {"memory_card":request.model_dump()}
        result = await MCmanager.amemory_card_polish(**input_)
        return MemoryCard(**result)

    except Exception as e:
        logger.error(f'{e} & {type(input_)} & {input_}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error Info: {e}",
        )

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, model_validator, field_validator, RootModel
import re

class MemoryCardGenerate(BaseModel):
    title: str = Field(..., description="标题",min_length=1, max_length=30)
    content: str = Field(..., description="内容",min_length=1,max_length=1000)
    time: str = Field(..., description="日期格式,YYYY年MM月DD日,其中YYYY可以是4位数字或4个下划线,MM可以是2位数字或2个--,DD可以是2位数字或2个--。年龄范围格式,X到Y岁,其中X和Y是数字。不接受 --到--岁")
    score: int = Field(..., description="卡片得分", ge=0, le=10)
    tag: str = Field(..., description="标签 max_length=4")
    topic: int = Field(..., description="主题1-5",ge=0, le=5)

    @field_validator('time')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        combined_regex = r"^(?:(\d{4}|-{4}|-{2})年(\d{2}|-{2})月(\d{2}|-{2})日|(\d+)到(\d+)岁|-{1,}到(\d+)岁|(\d+)到-{1,}岁)"
        match = re.match(combined_regex, v)
        if match:
            return v
        else:
            raise ValueError("时间无效")

class MemoryCardsGenerate(BaseModel):
    memory_cards: list[MemoryCardGenerate] = Field(..., description="记忆卡片列表")

class ChatHistoryOrText(BaseModel):
    text: str = Field(..., description="聊天内容或者文本内容",min_length=1,max_length=30000)
    birthday: str = Field(None, description="生日")
    age: str = Field(None, description="年龄")



@router.post("/generate_by_text",response_model=MemoryCardsGenerate,description="上传文件生成记忆卡片")
async def memory_card_generate_by_text_server(request: ChatHistoryOrText) -> dict:
    try:
        assert request.text
        input_ = {"chat_history_str":request.text,"birthday":request.birthday, "age":request.age}
        chapters = await MCmanager.agenerate_memory_card_by_text(**input_)
        return MemoryCardsGenerate(memory_cards=chapters)
    except AssertionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"MCmanager.agenerate_memory_card_by_text AssertError : {e}",
        )
    except Exception as e:
        logger.error(f'{e} & {type(input_)} & {input_}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error Info: {e}",
        )


@router.post("/generate",response_model=MemoryCardsGenerate,description="聊天历史生成记忆卡片")
async def memory_card_generate_server(request: ChatHistoryOrText) -> dict:
    try:
        assert request.text
        input_ = {"chat_history_str":request.text,"birthday":request.birthday, "age":request.age}
        chapters = await MCmanager.agenerate_memory_card(**input_)
        return MemoryCardsGenerate(memory_cards=chapters)

    except AssertionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"MCmanager.agenerate_memory_card. AssertError : {e}",
        )
    except Exception as e:
        logger.error(f'{e} & {type(input_)} & {input_}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error Info: {e}",
        )
