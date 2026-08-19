import re

from collections import Counter

from match_schema import (
    JDComparison,
    MatchReport,
    MultiJDReport,
)

SKILL_ALIASES = {
    "Python": ["python"],
    "Git": ["git"],
    "FastAPI": ["fastapi"],
    "RAG": ["rag", "检索增强生成"],
    "Embedding": ["embedding", "向量检索"],
    "Docker": ["docker", "容器化"],
    "SQL": ["sql", "结构化查询"],
    "Streamlit": ["streamlit"],
    "REST API": ["rest api", "http api", "接口"],
    "Prompt": ["prompt", "提示词"],
    "Pydantic": ["pydantic", "结构化输出"],
    "测试": ["pytest", "单元测试", "测试"],
}


PROJECT_SUGGESTIONS = {
    "SQL": "补充一个 SQL 数据分析 Agent 项目，展示只读查询和安全拦截",
    "Docker": "补充 Docker 部署和健康检查演示",
    "Embedding": "补充 Embedding 语义检索项目",
    "FastAPI": "补充 FastAPI 接口和 OpenAPI 文档演示",
    "测试": "补充自动化测试和评测指标",
    "Streamlit": "补充 Streamlit 数据展示页面",
    "REST API": "补充 REST API 接口设计、异常处理和接口测试项目",
}


def normalize_text(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        text.lower(),
    ).strip()


def find_skills(text: str) -> set[str]:
    normalized_text = normalize_text(text)
    found_skills = set()

    for skill, aliases in SKILL_ALIASES.items():
        if any(alias in normalized_text for alias in aliases):
            found_skills.add(skill)

    return found_skills


def calculate_score(
    matched_count: int,
    required_count: int,
) -> int:
    if required_count == 0:
        return 0

    return round(
        matched_count / required_count * 100
    )


def match_resume_to_jd(
    resume_text: str,
    jd_text: str,
) -> MatchReport:
    resume_skills = find_skills(resume_text)
    jd_skills = find_skills(jd_text)

    matched_skills = sorted(
        resume_skills.intersection(jd_skills)
    )
    missing_skills = sorted(
        jd_skills.difference(resume_skills)
    )

    projects_to_build = [
        PROJECT_SUGGESTIONS[skill]
        for skill in missing_skills
        if skill in PROJECT_SUGGESTIONS
    ]

    match_score = calculate_score(
        len(matched_skills),
        len(jd_skills),
    )

    if match_score >= 75:
        risk_level = "low"
    elif match_score >= 50:
        risk_level = "medium"
    else:
        risk_level = "high"

    explanation = (
        f"岗位识别到 {len(jd_skills)} 项技能，"
        f"简历已覆盖 {len(matched_skills)} 项，"
        f"当前匹配度为 {match_score}%。"
    )

    interview_risks = [
        f"需要准备 {skill} 的实际项目案例"
        for skill in missing_skills
    ]

    return MatchReport(
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        projects_to_build=projects_to_build,
        risk_level=risk_level,
        match_score=match_score,
        explanation=explanation,
        interview_risks=interview_risks,
    )


def main():
    resume_text = """
    熟悉 Python、Git、FastAPI、RAG、Embedding、Docker、
    Streamlit、Prompt、Pydantic 和自动化测试。
    """

    jd_text = """
    岗位要求：Python、FastAPI、RAG、Embedding、Docker、
    SQL、Streamlit 和测试经验。
    """

    report = match_resume_to_jd(
        resume_text,
        jd_text,
    )

    print(report.model_dump_json(
        indent=2,
        ensure_ascii=False,
    ))


def compare_resume_to_jds(
    resume_text: str,
    jd_items: list[dict],
) -> MultiJDReport:
    if not resume_text.strip():
        raise ValueError("简历内容不能为空")

    if not jd_items:
        raise ValueError("至少需要一份 JD")

    comparisons = []

    for item in jd_items:
        jd_name = str(
            item.get("name", "")
        ).strip()
        jd_text = str(
            item.get("jd", "")
        ).strip()

        if not jd_name:
            raise ValueError("岗位名称不能为空")

        if not jd_text:
            raise ValueError(
                f"岗位 {jd_name} 的 JD 不能为空"
            )

        report = match_resume_to_jd(
            resume_text,
            jd_text,
        )

        comparisons.append(
            JDComparison(
                jd_name=jd_name,
                report=report,
            )
        )

    sorted_comparisons = sorted(
        comparisons,
        key=lambda item: (
            -item.report.match_score,
            item.jd_name,
        ),
    )

    best_match = sorted_comparisons[0].jd_name

    missing_counter = Counter(
        skill
        for comparison in comparisons
        for skill in comparison.report.missing_skills
    )

    common_missing_skills = sorted(
        skill
        for skill, count in missing_counter.items()
        if count >= 2
    )

    if common_missing_skills:
        missing_text = "、".join(
            common_missing_skills
        )
        recommendation = (
            f"优先投递 {best_match}，"
            f"并优先补强多份 JD 共同要求的"
            f" {missing_text}。"
        )
    else:
        recommendation = (
            f"优先投递 {best_match}。"
            "当前没有重复出现的技能缺口，"
            "可分别准备各岗位的专项能力。"
        )

    return MultiJDReport(
        comparisons=sorted_comparisons,
        best_match=best_match,
        common_missing_skills=common_missing_skills,
        recommendation=recommendation,
    )

 
if __name__ == "__main__":
    main()