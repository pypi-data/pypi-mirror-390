# server
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from digital_life.server.router.digital_avatar.digital_avatar_router import router as avatar_router
from digital_life.server.router.memory_card.memory_card_router import router as memory_card_router
from digital_life.server.router.recommend.recommended import router as recommended_router
from digital_life.server.router.biography.biography_router import router as biography_router
from digital_life.server.router.user.user_router import router as user_router
from digital_life.server.router.chat.chat_router import router as chat_router
from pro_craft.server.router.prompt import create_router
from fastapi import FastAPI, HTTPException, status
import os
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, model_validator, field_validator, RootModel
import re
import inspect
from digital_life import logger
import os
import math

app = FastAPI(
    title="LLM Service",
    description="Provides an OpenAI-compatible API for custom large language models.",
    version="1.0.1",
)

# --- Configure CORS ---
origins = [
    "*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specifies the allowed origins
    allow_credentials=True,  # Allows cookies/authorization headers
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers (Content-Type, Authorization, etc.)
)
# --- End CORS Configuration ---

database_url = os.getenv("database_url")

                             
prompt_router = create_router(database_url=database_url,
              slave_database_url=database_url + "-test",
              model_name="doubao-1-5-pro-256k-250115",
              logger=logger)

prompt_inner_router = create_router(database_url=database_url,
              slave_database_url=os.getenv("product_database_url"),
              model_name="doubao-1-5-pro-256k-250115",
              logger=logger)

app.include_router(avatar_router, prefix="/digital_avatar")
app.include_router(memory_card_router, prefix="/memory_card")
app.include_router(recommended_router, prefix="/recommended")
app.include_router(prompt_router, prefix="/prompt")
app.include_router(prompt_inner_router, prefix="/prompt_inner")
app.include_router(chat_router, prefix="/v1")
app.include_router(biography_router)
app.include_router(user_router)


async def get_score_overall(
    S: list[int], total_score: int = 0, epsilon: float = 0.001, K: float = 0.8
) -> float:
    """
    计算 y = sqrt(1/600 * x) 的值。
    计算人生总进度
    """
    x = sum(S)
    
    S_r = [math.sqrt((1/101) * i)/5 for i in S]
    return sum(S_r) * 100

    # return math.sqrt((1/601) * x)  * 100


async def get_score(
    S: list[int], total_score: int = 0, epsilon: float = 0.001, K: float = 0.01
) -> float:
    # 人生主题分值计算
    # 一个根据 列表分数 计算总分数的方法 如[1,4,5,7,1,5] 其中元素是 1-10 的整数
    # 一个非常小的正数，确保0分也有微弱贡献，100分也不是完美1
    # 调整系数，0 < K <= 1。K越大，总分增长越快。

    for score in S:
        normalized_score = (score + epsilon) / (10 + epsilon)
        total_score = total_score + (100 - total_score) * normalized_score * K
        if total_score >= 100 - 1e-9:  
            total_score = 100 - 1e-9
            break 

    return total_score



@app.get("/")
async def root():
    """server run"""
    envs = {
        "host":os.getenv("host"),
        "port":os.getenv("port"),
        "similarity_top_k":os.getenv("similarity_top_k"),
        "similarity_cutoff":os.getenv("similarity_cutoff"),
        "collection_name":os.getenv("collection_name"),
        "api_key":os.getenv("api_key"),
        "model_name":os.getenv("model_name"),
        "llm_model_name":os.getenv("llm_model_name"),
        "llm_api_key":os.getenv("llm_api_key"),
        "recommended_biographies_cache_max_leng":os.getenv("recommended_biographies_cache_max_leng"),
        "recommended_cache_max_leng":os.getenv("recommended_cache_max_leng"),
        "user_callback_url":os.getenv("user_callback_url"),
        "card_weight":os.getenv("card_weight"),
    }

    return {"message": "LLM Service is running.",
            "envs":envs}

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


@app.post("/life_topic_score")
async def life_topic_score_server(request: LifeTopicScoreRequest):
    try:
        result = await get_score(
            S=request.S_list,
            total_score=request.total_score,
            epsilon=request.epsilon,
            K=request.K,
        )
        return {
            "message": "Life topic score calculated successfully",
            "result": int(result),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        frame = inspect.currentframe()
        info = inspect.getframeinfo(frame)
        logger.error(f"Error: & {info.function} & {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Function name: {info.function} : {e}",
        )


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


@app.post("/life_aggregate_scheduling_score")
async def life_aggregate_scheduling_score_server(request: ScoreRequest):
    try:
        result = await get_score_overall(
            request.S_list,
            total_score=request.total_score,
            epsilon=request.epsilon,
            K=request.K,
        )
        return {
            "message": "life aggregate scheduling score successfully",
            "result": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        frame = inspect.currentframe()
        info = inspect.getframeinfo(frame)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Function name: {info.function} : {e}",
        )


if __name__ == "__main__":
    import argparse
    import uvicorn

    default = 8007
    
    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        "port",
        metavar="PORT",
        type=int,
        nargs="?",  # 端口是可选的
        default=default,
        help=f"Specify alternate port [default: {default}]",
    )
    # 创建一个互斥组用于环境选择
    group = parser.add_mutually_exclusive_group()

    # 添加 --dev 选项
    group.add_argument(
        "--dev",
        action="store_true",  # 当存在 --dev 时，该值为 True
        help="Run in development mode (default).",
    )

    # 添加 --prod 选项
    group.add_argument(
        "--prod",
        action="store_true",  # 当存在 --prod 时，该值为 True
        help="Run in production mode.",
    )
    args = parser.parse_args()

    if args.prod:
        env = "prod"
    else:
        # 如果 --prod 不存在，默认就是 dev
        env = "dev"

    port = args.port

    if env == "dev":
        port += 100
        reload = True
        app_import_string = (
            f"{__package__}.__main__:app"  # <--- 关键修改：传递导入字符串
        )
    elif env == "prod":
        reload = False
        app_import_string = app
    else:
        reload = False
        app_import_string = app

    # 使用 uvicorn.run() 来启动服务器
    # 参数对应于命令行选项
    uvicorn.run(
        app_import_string, host="0.0.0.0", port=port, reload=reload  # 启用热重载
    )
