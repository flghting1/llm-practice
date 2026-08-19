from matcher import compare_resume_to_jds


RESUME_TEXT = """
熟悉 Python、Git、FastAPI、RAG、Embedding、Docker、
Streamlit、Prompt、Pydantic 和自动化测试。
"""

JD_ITEMS = [
    {
        "name": "RAG 应用开发岗位",
        "jd": """
        要求 Python、FastAPI、RAG、Embedding、
        Docker、SQL 和测试经验。
        """,
    },
    {
        "name": "后端 API 开发岗位",
        "jd": """
        要求 Python、FastAPI、Git、
        REST API 和 Docker。
        """,
    },
    {
        "name": "数据分析开发岗位",
        "jd": """
        要求 Python、SQL、Streamlit 和测试经验。
        """,
    },
]


def main():
    result = compare_resume_to_jds(
        RESUME_TEXT,
        JD_ITEMS,
    )

    assert len(result.comparisons) == 3
    assert result.best_match == "RAG 应用开发岗位"
    assert "SQL" in result.common_missing_skills

    scores = [
        item.report.match_score
        for item in result.comparisons
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )

    print("多 JD 数量：", len(result.comparisons))
    print("最佳匹配岗位：", result.best_match)
    print(
        "共同技能缺口：",
        result.common_missing_skills,
    )

    for comparison in result.comparisons:
        print(
            comparison.jd_name,
            comparison.report.match_score,
            comparison.report.missing_skills,
        )

    print("综合建议：", result.recommendation)
    print("\n多 JD 对比测试全部通过")


if __name__ == "__main__":
    main()