
# server
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, model_validator, field_validator, RootModel
import re


# 分数

class LifeTopicScoreRequest(BaseModel):
    S_list: List[int] = Field(..., description="List of scores, each between 1 and 10.")
    K: float = Field(0.8, description="Weighting factor K.")
    total_score: int = Field(0, description="Initial total score.")
    epsilon: float = Field(0.001, description="Epsilon value for calculation.")

    @model_validator(mode="after")
    def validate_s_list(self):
        if not all(0 <= x <= 10 for x in self.S_list):
            raise ValueError(
                "All elements in 'S_list' must be integers between 1 and 10 (inclusive)."
            )
        return self

class ScoreRequest(BaseModel):
    S_list: List[float] = Field(
        ...,
        description="List of string representations of scores, each between 1 and 10.",
    )
    K: float = Field(0.3, description="Coefficient K for score calculation.")
    total_score: int = Field(0, description="Total score to be added.")
    epsilon: float = Field(0.0001, description="Epsilon value for score calculation.")

    @model_validator(mode="after")
    def check_s_list_values(self):
        for s_val in self.S_list:
            try:
                int_s_val = float(s_val)
                if not (0 <= int_s_val <= 100):
                    raise ValueError(
                        "Each element in 'S_list' must be an integer between 1 and 10."
                    )
            except ValueError:
                raise ValueError(
                    "Each element in 'S_list' must be a valid integer string."
                )
        return self


# 记忆卡片
class MemoryCardsRequest(BaseModel):
    memory_cards: list[str] = Field(..., description="记忆卡片列表")

class MemoryCard(BaseModel):
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    time: str = Field(..., description="卡片记录事件的发生时间")

class MemoryCard2(BaseModel):
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    time: str = Field(..., description="卡片记录事件的发生时间")
    tag: str = Field(..., description="标签1",max_length=4)


class MemoryCardScore(BaseModel):
    score: int = Field(..., description="得分")
    reason: str = Field(..., description="给分理由")


class MemoryCards(BaseModel):
    memory_cards: list[MemoryCard] = Field(..., description="记忆卡片列表")

class MemoryCardGenerate2(BaseModel):
    title: str = Field(..., description="标题",min_length=1, max_length=30)
    content: str = Field(..., description="内容",min_length=1,max_length=1000)
    time: str = Field(..., description="日期格式,YYYY年MM月DD日,其中YYYY可以是4位数字或4个下划线,MM可以是2位数字或2个--,DD可以是2位数字或2个--。年龄范围 输出对应的文字描述, 比如:而立, 不惑")
    score: int = Field(..., description="卡片得分", ge=0, le=10)
    tag: str = Field(..., description="标签1",max_length=4)
    topic: int = Field(..., description="主题1-5",ge=0, le=5)

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

class MemoryCardGenerateEasy(BaseModel):
    title: str = Field(..., description="标题",min_length=1, max_length=30)
    content: str = Field(..., description="内容",min_length=1,max_length=1000)
    time: str = Field(..., description="日期格式,YYYY年MM月DD日,其中YYYY可以是4位数字或4个下划线,MM可以是2位数字或2个--,DD可以是2位数字或2个--。年龄范围格式,X到Y岁,其中X和Y是数字。不接受 --到--岁")
    score: int = Field(..., description="卡片得分", ge=0, le=10)
    tag: str = Field(..., description="标签1",max_length=4)
    topic: int = Field(..., description="主题1-7",ge=0, le=7)

    @field_validator('time')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        combined_regex = r"^(?:(\d{4}|-{4}|-{2})年(\d{2}|-{2})月(\d{2}|-{2})日|(\d+)到(\d+)岁|-{2}到-{2}岁|-{1,}到(\d+)岁|(\d+)到-{1,}岁)$"
        match = re.match(combined_regex, v)
        if match:
            return v
        else:
            raise ValueError("时间无效")

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
        combined_regex = r"^(?:(\d{4}|-{4}|-{2})年(\d{2}|-{2})月(\d{2}|-{2})日|(\d+)到(\d+)岁|-{1,}到(\d+)岁|(\d+)到-{1,}岁)$"
        match = re.match(combined_regex, v)
        if match:
            return v
        else:
            raise ValueError("时间无效")

class MemoryCardsGenerate(BaseModel):
    memory_cards: list[MemoryCardGenerate] = Field(..., description="记忆卡片列表")

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


# 分身
class PersonInfo(BaseModel):
    """
    表示一个人的详细信息。
    """
    relationship: str = Field(..., description="与查询对象的_关系_")
    profession: str = Field(..., description="职业信息")
    birthday: str = Field(..., description="生日信息 (格式可根据实际情况调整)")

class CharactersData(RootModel[Dict[str, PersonInfo]]):
    """
    表示一个包含多个角色信息的字典，键为角色名称，值为 PersonInfo 模型。
    """
    pass # RootModel 不需要定义额外的字段，它直接代理其泛型类型

class ContentVer(BaseModel):
    content: str = Field(..., description="内容")

# 传记




class Extract_Person(BaseModel):
    content: list[str] = Field(..., description="提取人名")

class Extract_Place(BaseModel):
    content: list[str] = Field(..., description="提取地名")

class Biography_Free(BaseModel):
    title: str = Field(..., description="标题")
    description: str = Field(..., description="传记的简介")
    content: str = Field(..., description="传记正文")

class ContentVer(BaseModel):
    content: str = Field(..., description="内容")


class MemoryCard_biograph(BaseModel):
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    time: str = Field(..., description="卡片记录事件的发生时间")
    theme_id: str = Field(None, description="theme_id")

class BiographyRequest(BaseModel):
    """
    请求传记生成的数据模型。
    """

    user_name: str = Field(None, description="用户名字")
    vitae: str = Field(None, description="用户简历")
    memory_cards: list[MemoryCard_biograph] = Field(..., description="记忆卡片列表")
    # 可以在这里添加更多用于生成传记的输入字段


class UseroverviewRequests(BaseModel):
    action: str
    old_overview: str
    memory_cards: list[MemoryCard]


class AvatarXGRequests(BaseModel):
    action: str
    old_character: str
    memory_cards: list[MemoryCard]


class ChatHistoryOrText(BaseModel):
    text: str = Field(..., description="聊天内容或者文本内容",min_length=1,max_length=30000)



class UserRelationshipExtractionRequest(BaseModel):
    text: str


class BriefResponse(BaseModel):
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    tags: list[str] = Field(..., description='["标签1","标签2"]')


class DeleteRequest(BaseModel):
    id: str


class DeleteResponse(BaseModel):
    status: str = "success"  # 假设返回一个状态表示删除成功


class UpdateItem(BaseModel):
    text: str = Field(
        ..., min_length=1, max_length=2000, description="要更新的文本内容。"
    )
    id: str = Field(
        ..., min_length=1, max_length=100, description="与文本关联的唯一ID。"
    )
    type: int = Field(..., description="上传的类型")


class QueryItem(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=500, description="user_id")
    timestamp: str = Field(..., min_length=1, max_length=500, description="timestamp")
    current: int
    size: int


class BiographyResult(BaseModel):
    """
    传记生成结果的数据模型。
    """

    task_id: str = Field(..., description="任务的唯一标识符。")
    status: str = Field(
        ...,
        description="任务的当前状态 (e.g., 'PENDING', 'PROCESSING', 'COMPLETED', 'FAILED').",
    )
    biography_title: Optional[str] = Field(None, description="传记标题")

    biography_brief: Optional[str] = Field(
        None, description="生成的传记简介，仅在状态为 'COMPLETED' 时存在。"
    )
    biography_json: dict | None = Field(
        None, description="生成的传记文本，仅在状态为 'COMPLETED' 时存在。"
    )
    biography_name: list[str] | None = Field(
        None, description="生成的传记文本中的人名，仅在状态为 'COMPLETED' 时存在。"
    )
    biography_place: list[str] | None = Field(
        None, description="生成的传记文本中的地名，仅在状态为 'COMPLETED' 时存在。"
    )
    error_message: Optional[str] = Field(
        None, description="错误信息，仅在状态为 'FAILED' 时存在。"
    )
    progress: float = Field(
        0.0, ge=0.0, le=1.0, description="任务处理进度，0.0到1.0之间。"
    )
