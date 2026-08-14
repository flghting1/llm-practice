from time import perf_counter

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator


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

    return ChatResponse(
        answer=f"你提出的问题是：{request.question}",
        sources=["local-demo"],
        latency_ms=round((perf_counter() - start_time) * 1000, 2),
    )