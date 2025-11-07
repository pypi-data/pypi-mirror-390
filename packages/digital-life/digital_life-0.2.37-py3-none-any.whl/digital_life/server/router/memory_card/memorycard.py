# 1 日志不打在server中 不打在工具中, 只打在core 中

import math
import asyncio
from pro_craft import AsyncIntel
from pro_craft.utils import create_async_session
from digital_life.utils import memoryCards2str
# server
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, model_validator, field_validator, RootModel
import re
from digital_life import logger
import os
from pro_craft.utils import extract_
import json

class AIServerInputError(Exception):
    pass



class MemoryCard2(BaseModel):
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    time: str = Field(..., description="卡片记录事件的发生时间")
    tag: str = Field(..., description="标签1,max_length=4")




# 1. 定义记忆卡片模型 (Chapter)
class Chapter(BaseModel):
    """
    表示文档中的一个记忆卡片（章节）。
    """
    title: str = Field(..., description="记忆卡片的标题")
    content: str = Field(..., description="记忆卡片的内容")

# 2. 定义整个文档模型 (Document)
class Document(BaseModel):
    """
    表示一个包含标题和多个记忆卡片的文档。
    """
    title: str = Field(..., description="整个文档的标题内容")
    chapters: List[Chapter] = Field(..., description="文档中包含的记忆卡片列表")


class MemoryCardGenerate(BaseModel):
    title: str = Field(..., description="标题",min_length=1, max_length=30)
    content: str = Field(..., description="内容",min_length=1,max_length=1000)
    time: str = Field(..., description="日期格式,YYYY年MM月DD日,其中YYYY可以是4位数字或4个下划线,MM可以是2位数字或2个--,DD可以是2位数字或2个--。年龄范围格式,X到Y岁,其中X和Y是数字。不接受 --到--岁")
    score: int = Field(..., description="卡片得分", ge=0, le=10)
    tag: str = Field(..., description="标签1",max_length=4)
    topic: int = Field(..., description="主题1-7",ge=0, le=7)

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

class TimeCheck(BaseModel):
    time: str = Field(...,description="")
    @field_validator('time')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        combined_regex = r"^(?:(\d{4}|-{4}|-{2})年(\d{2}|-{2})月(\d{2}|-{2})日)"
        match = re.match(combined_regex, v)
        if match:
            return v
        elif v in ["稚龄","少年","弱冠","而立","不惑","知天命","耳顺","古稀","耄耋","鲐背","期颐"]:
            return v
        else:
            raise ValueError("时间无效")
doc = {"稚龄":"0到10岁",
    "少年":"11到20岁",
    "弱冠":"21到30岁",
    "而立":"31到40岁",
    "不惑":"41到50岁",
    "知天命":"51到60岁",
    "耳顺":"61到70岁",
    "古稀":"71到80岁",
    "耄耋":"81到90岁",
    "鲐背":"91到100岁",
    "期颐":"101到110岁"} 


class MemoryCardManager:
    def __init__(self,inference_save_case = False,model_name  = ""):
        self.inters = AsyncIntel(model_name = model_name,logger = logger)
        self.inference_save_case = inference_save_case

    async def ascore_from_memory_card(self, memory_cards: list[str]) -> list[int]:
        logger.info(f'函数输入 & {type(memory_cards)} &  {memory_cards}')
        class MemoryCardScore(BaseModel):
            score: int = Field(..., description="得分")
            reason: str = Field(..., description="给分理由")

        result = await self.inters.inference_format_gather(
            input_datas=memory_cards,
            prompt_id = "memorycard-score",
            version = None,
            OutputFormat = MemoryCardScore,
        )
        logger.info(f'函数输出 & {type(result)} &  {result}')
        return result

    async def amemory_card_merge(self, memory_cards: list[str]):
        logger.info(f'函数输入 & {type(memory_cards)} &  {memory_cards}')

        class MemoryCard(BaseModel):
            title: str = Field(..., description="标题")
            content: str = Field(..., description="内容")
            time: str = Field(..., description="卡片记录事件的发生时间")
            tag: str = Field(..., description="标签1,max_length=4")


        result = await self.inters.inference_format(
            input_data=memory_cards,
            prompt_id = "memorycard-merge",
            version = None,
            OutputFormat = MemoryCard,
        )
        time = await self.get_time(result.get("content"))
        result.update({"time":time})
        
        logger.info(f'函数输出 & {type(result)} &  {result}')
        return result

    async def amemory_card_polish(self, memory_card: dict) -> dict:
        logger.info(f'函数输入 & {type(memory_card)} &  {memory_card}')

        class MemoryCardArticle(BaseModel):
            title: str = Field(..., description="标题")
            content: str = Field(..., description="内容")

        result = await self.inters.inference_format(
            input_data=memory_card,
            prompt_id = "memorycard-polish",
            version = None,
            OutputFormat = MemoryCardArticle,
        )
        logger.info(f'函数输出 & {type(result)} &  {result}')
        return result

    def _generate_check(self,chat_history_str):
        if "human" not in chat_history_str:
            raise AIServerInputError("聊天历史生成记忆卡片时, 必须要有用户的输入信息")
        
        if "ai" in chat_history_str:
            chat_history_str = "human" + chat_history_str.split("human",1)[-1]
            chat_history_str = chat_history_str.rsplit("ai:",1)[0]
        return chat_history_str
    
    async def get_time(self,content,brithday = '',age = ''):
        result_time = "----年--月--日"
        # 先做一个年月日格式的生成

        class TimeCheck_1(BaseModel):
            time: str = Field(...,description="----年--月--日")
            reason: str = Field(...,description="推理原因")
            @field_validator('time')
            @classmethod
            def validate_time_format(cls, v: str) -> str:
                combined_regex = r"^(?:(\d{4}|-{4}|-{2})年(\d{2}|-{2})月(\d{2}|-{2})日)"
                match = re.match(combined_regex, v)
                if match:
                    return v
                else:
                    raise ValueError("时间无效")

        from datetime import datetime
        now_str = datetime.now().strftime("%Y年%m月%d日")
        print(now_str,'now_str')
        result_time_dict = await self.inters.inference_format(
            input_data={
                            "出生时间": brithday,
                            "now_time": now_str,
                            "content": content
                        },
            prompt_id = "memorycard-get-time",
            version=None,
            OutputFormat=TimeCheck_1,
            )
        result_time = result_time_dict.get("time","----年--月--日")

        logger.info(f'get_time 函数第一次输出 & {type(result_time)} &  {result_time}')
        
        if "--年--月--日" in result_time: # 说明没有检测出具体的时间

            class TimeCheck_2(BaseModel):
                stage: str = Field(...,description="根据发生的事件推测其发生的阶段")
                reason: str = Field(...,description="推理原因")
                @field_validator('stage')
                @classmethod
                def validate_time_format(cls, v: str) -> str:
                    if v in ["稚龄","少年","弱冠","而立","不惑","知天命","耳顺","古稀","耄耋","鲐背","期颐"]:
                        return v
                    else:
                        raise ValueError("时间无效")
                    
            ai_result_time = await self.inters.inference_format(
                input_data={
                            "当前年龄": age,
                            "content": content
                        },
                prompt_id = "memorycard-get-timeline",
                version=None,
                OutputFormat= TimeCheck_2,
                )
            stage = ai_result_time.get("stage","而立")
            result_time = doc[stage]

        logger.info(f'get_time 函数输出 & {type(result_time)} &  {result_time}')
        
        return result_time

    async def agenerate_memory_card_by_text(self, chat_history_str: str, birthday: str, age : str):
        weight=int(os.getenv("card_weight",1000))
        logger.info(f'函数输入 & {type(chat_history_str)} &  {chat_history_str} weight: {weight}')
        number_ = len(chat_history_str) // weight + 1

        class Chapter(BaseModel):
            """
            表示文档中的一个记忆卡片（章节）。
            """
            title: str = Field(..., description="标题title")
            content: str = Field(..., description="正文 content")

        class DocumentOutput(BaseModel):
            title: str = Field(..., description="整个文档的标题内容")
            chapters: List[Chapter] = Field(..., description="文档中包含的记忆卡片列表")
        
        result_dict = await self.inters.inference_format(
            input_data={"建议输出卡片数量":  number_, "chat_history_str": chat_history_str},
            prompt_id = "memorycard-generate-content",
            version=None,
            OutputFormat= DocumentOutput,
            )
        chapters = result_dict["chapters"]

        if [chapter.get("content") for chapter in chapters] == [""]:
            raise AIServerInputError("没有记忆卡片生成")
        
        # 生成最初的文本
        logger.info(f'chapters & {type(chapters)} &  {chapters}')

        class MemoryCardGenerate(BaseModel):
            title: str = Field(..., description="标题",min_length=1, max_length=30)
            content: str = Field(..., description="内容",min_length=1,max_length=1000)
            score: int = Field(..., description="卡片得分", ge=0, le=10)
            tag: str = Field(..., description="标签1, max_length=4")
            time: str = Field(..., description="日期格式,YYYY年MM月DD日,其中YYYY可以是4位数字或4个下划线,MM可以是2位数字或2个--,DD可以是2位数字或2个--。年龄范围 输出对应的文字描述, 比如:而立, 不惑")
            topic: int = Field(..., description="主题1-5",ge=0, le=5)

        chapters_with_tags = await self.inters.inference_format_gather(
                input_datas=[chapter for chapter in chapters],
                prompt_id = "memorycard-format",
                version = None,
                OutputFormat = MemoryCardGenerate,
            )

        logger.info(f'chapters_with_tags & {type(chapters_with_tags)} &  {chapters_with_tags}')
        # [{'title': '牵引空客A380', 'content': '我是白云机场机坪操作部的牵引车司机，2023年的一天，要牵引一架即将执飞国际航线的空客A380。每次靠近它都能感受到压迫力与使命感。抵达远程停机位时，飞机还在夜色中沉睡，机务工程师们已在机腹下忙碌，橙色警示灯闪烁，机坪上空寂寥，只有风声和远处跑道飞机起降的轰鸣。我跳下牵引车，仔细与机务负责人核对信息、检查牵引连接点，深知每个操作关乎数百人的旅行计划与安全。', 'time': '2023年--月--日', 'score': 7, 'tag': '牵引飞机', 'topic': 3}, {'title': '机场紧急牵引任务', 'content': '在机场工作，紧张时刻家常便饭。最让我印象深刻且紧张的一次，是在一个雷雨交加的夜晚。一架航班遭遇强烈乱流，机上一名旅客突发急病紧急降落，降落时轮胎受损需牵引。接到任务时，狂风暴雨，电闪雷鸣，机坪能见度极低，塔台焦急强调飞机上有急需救援的病人。我驾驶牵引车冲进雨幕，雨刮器开到最大也几乎看不清路。平时牵引普通航班时间充裕，可这次每分每秒都至关重要，我必须快速抵达飞机且确保安全。', 'time': '未知', 'score': 7, 'tag': '紧急任务', 'topic': 3}] info_dicts


        for chapter_with_tag in chapters_with_tags:
            time = await self.get_time(chapter_with_tag.get("content"), birthday, age)
            chapter_with_tag.update({"time":time})


        logger.info(f'chapters_with_time & {type(chapters_with_tags)} &  {chapters_with_tags}')

        # for i,chapter in enumerate(chapters):
        #     chapter.update(chapters_with_tags[i])
        
        # for chapter in chapters:
        #     try:
        #         MemoryCardsGenerate(memory_cards=[chapter])
        #     except Exception as e:
        #         # super_log(f"{e}",'agenerate_memory_card Error')
        #         chapter.update({"time":"----年--月--日"})
        #     if len(chapter.get("tag")) >4:
        #         chapter.update({"tag":""})

        result = chapters_with_tags
        logger.info(f'函数输出 & {type(result)} &  {result}')
        
        return result
    
    async def agenerate_memory_card(self, chat_history_str: str,birthday: str, age : str):
        chat_history_str = self._generate_check(chat_history_str)
        result = await self.agenerate_memory_card_by_text(chat_history_str = chat_history_str, birthday = birthday, age = age)
        return result


# ----年11月--日至次年02月--日