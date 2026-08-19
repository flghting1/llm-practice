from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from matcher import (
    compare_resume_to_jds,
    match_resume_to_jd,
)


app = FastAPI(
    title="简历与 JD 匹配助手",
    version="0.2.0",
)


class MatchRequest(BaseModel):
    resume_text: str = Field(
        min_length=1,
        description="简历文本",
    )
    jd_text: str = Field(
        min_length=1,
        description="岗位 JD 文本",
    )


class JDItem(BaseModel):
    name: str = Field(
        min_length=1,
        description="岗位名称",
    )
    jd: str = Field(
        min_length=1,
        description="岗位 JD",
    )


class CompareRequest(BaseModel):
    resume_text: str = Field(
        min_length=1,
        description="简历文本",
    )
    jd_items: list[JDItem] = Field(
        min_length=1,
        description="多个岗位 JD",
    )


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "resume-matcher",
    }


@app.post("/match")
def match(request: MatchRequest):
    resume_text = request.resume_text.strip()
    jd_text = request.jd_text.strip()

    if not resume_text:
        raise HTTPException(
            status_code=400,
            detail="简历内容不能为空",
        )

    if not jd_text:
        raise HTTPException(
            status_code=400,
            detail="JD 内容不能为空",
        )

    try:
        report = match_resume_to_jd(
            resume_text,
            jd_text,
        )
        return report.model_dump()

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@app.post("/compare")
def compare(request: CompareRequest):
    resume_text = request.resume_text.strip()

    if not resume_text:
        raise HTTPException(
            status_code=400,
            detail="简历内容不能为空",
        )

    try:
        result = compare_resume_to_jds(
            resume_text,
            [
                item.model_dump()
                for item in request.jd_items
            ],
        )
        return result.model_dump()

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error