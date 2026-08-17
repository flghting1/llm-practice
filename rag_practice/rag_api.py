from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from rag_answer import answer_question


app = FastAPI(
    title="RAG Knowledge API",
    version="1.0.0",
)


class AskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=500,
    )


class SourceItem(BaseModel):
    title: str
    source: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceItem]


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post(
    "/ask",
    response_model=AskResponse,
)
def ask(request: AskRequest) -> dict:
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="question 不能为空",
        )

    result = answer_question(question)

    return {
        "answer": result["answer"],
        "sources": result["sources"],
    }