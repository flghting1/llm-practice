import logging
import os
from time import perf_counter

from fastapi import FastAPI, Header,HTTPException
from pydantic import BaseModel, Field, field_validator


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)
app = FastAPI(title="HTTP Practice API")


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=200)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("question 不能只包含空格")

        return cleaned_value


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    latency_ms: float


@app.get("/health")
def health_check():
    return {"ok": True}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if request.question == "test-400":
        raise HTTPException(
            status_code=400,
            detail="这是用于演示 400 状态码的请求",
        )

    start_time = perf_counter()

    logger.info(
        "收到 chat 请求，question_length=%s",
        len(request.question),
    )

    try:
        response = ChatResponse(
            answer=f"你提出的问题是：{request.question}",
            sources=["local-demo"],
            latency_ms=round(
                (perf_counter() - start_time) * 1000,
                2,
            ),
        )
    except Exception as error:
        logger.exception("处理 chat 请求失败")
        raise HTTPException(
            status_code=500,
            detail="服务内部发生错误",
        ) from error

    logger.info(
        "chat 请求完成，latency_ms=%s",
        response.latency_ms,
    )

    return response

@app.get("/admin/stats")
def admin_stats(
    x_api_key:str | None = Header(default=None),
):
    excepted_api_key = os.getenv("DEMO_API_KEY")

    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="缺少 API Key",
        )

    if x_api_key != excepted_api_key:
        raise HTTPException(
            status_code=403,
            detail="API Key 不正确",
        )

    return {
        "users":10,
        "questions":25,
        "status":"ok",
    }

USERS = {
    1: {"name": "张三","role": "developer"},
    2: {"name": "李四","role": "tester"},
}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = USERS.get(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户不存在",
        )

    return {
        "id": user_id,
        **user,
    }