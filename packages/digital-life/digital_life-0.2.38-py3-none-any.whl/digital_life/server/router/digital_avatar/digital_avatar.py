#
import asyncio
from pro_craft import AsyncIntel
from digital_life.models import PersonInfo, CharactersData, ContentVer, BriefResponse
from digital_life.utils import memoryCards2str, extract_article
from digital_life import inference_save_case
import pandas as pd

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, model_validator, field_validator, RootModel
import re
###

class DigitalAvatar:
    def __init__(self,inference_save_case = False,model_name = "doubao-1-5-pro-256k-250115"):
        self.inters = AsyncIntel(model_name = model_name)
        self.inference_save_case = inference_save_case


    async def desensitization(self, memory_cards: list[str]) -> list[str]:
        """
        数字分身脱敏 0100
        0100
        """
        results = await self.inters.inference_format_gather(
            input_datas=memory_cards,
            prompt_id="avatar-desensitization",
            version=None,
            OutputFormat=ContentVer,
        )

        for i, memory_card in enumerate(memory_cards):
            memory_card["content"] = results[i].get("content")
        return memory_cards
    
    async def personality_extraction(self, memory_cards: list[dict],action:str,old_character:str) -> str:

        result = await self.inters.inference_format(
                                    input_data={
                                                "action": action,
                                                "old_character": old_character,
                                                "memory_cards": memory_cards
                                            },
                                    prompt_id ="avatar-personality-extraction",
                                    version = None,
                                    OutputFormat="",
                                    )
        
        return result

    async def abrief(self, memory_cards: list[dict]) -> dict:
        class BriefResponse(BaseModel):
            title: str = Field(..., description="标题")
            content: str = Field(..., description="内容")
            tags: list[str] = Field(..., description='["标签1","标签2"]')

        result = await self.inters.inference_format(
                                input_data={
                                    "memory_cards": memory_cards
                                },
                                prompt_id="avatar-brief",
                                version = None,
                                OutputFormat = BriefResponse,
                                 )
        return result



