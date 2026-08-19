from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from sql_agent import ask_database


app = FastAPI(
    title="SQL 数据分析 Agent",
    version="0.1.0",
)


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "sql-agent",
    }


@app.post("/ask")
def ask(request: AskRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="问题不能为空",
        )

    try:
        return ask_database(question)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error