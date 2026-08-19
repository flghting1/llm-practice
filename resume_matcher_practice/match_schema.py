from typing import Literal

from pydantic import BaseModel, Field


class MatchReport(BaseModel):
    matched_skills: list[str] = Field(
        default_factory=list,
        description="简历中已经具备的岗位技能",
    )
    missing_skills: list[str] = Field(
        default_factory=list,
        description="岗位要求但简历中缺少的技能",
    )
    projects_to_build: list[str] = Field(
        default_factory=list,
        description="建议补充或强化的项目",
    )
    risk_level: Literal[
        "low",
        "medium",
        "high",
    ] = Field(
        description="岗位匹配风险等级",
    )
    match_score: int = Field(
        ge=0,
        le=100,
        description="岗位匹配分数，范围 0 到 100",
    )
    explanation: str = Field(
        min_length=1,
        description="匹配结果的简要解释",
    )
    interview_risks: list[str] = Field(
        default_factory=list,
        description="可能被面试官追问的风险点",
    )
class JDComparison(BaseModel):
    jd_name: str = Field(
        min_length=1,
        description="岗位名称",
    )
    report: MatchReport


class MultiJDReport(BaseModel):
    comparisons: list[JDComparison]
    best_match: str = Field(
        min_length=1,
        description="匹配分数最高的岗位",
    )
    common_missing_skills: list[str] = Field(
        default_factory=list,
        description="多份 JD 中重复出现的技能缺口",
    )
    recommendation: str = Field(
        min_length=1,
        description="岗位选择和补强建议",
    )