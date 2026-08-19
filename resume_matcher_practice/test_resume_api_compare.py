from fastapi.testclient import TestClient

from resume_api import app


client = TestClient(app)

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
    response = client.post(
        "/compare",
        json={
            "resume_text": RESUME_TEXT,
            "jd_items": JD_ITEMS,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert len(result["comparisons"]) == 3
    assert result["best_match"] == "RAG 应用开发岗位"
    assert "SQL" in result["common_missing_skills"]
    assert result["recommendation"]

    print("多 JD 接口：通过")
    print("岗位数量：", len(result["comparisons"]))
    print("最佳岗位：", result["best_match"])
    print(
        "共同技能缺口：",
        result["common_missing_skills"],
    )
    print("综合建议：", result["recommendation"])

    empty_response = client.post(
        "/compare",
        json={
            "resume_text": RESUME_TEXT,
            "jd_items": [],
        },
    )

    assert empty_response.status_code == 422
    print("空 JD 列表校验：通过")

    print("\n多 JD FastAPI 接口测试全部通过")


if __name__ == "__main__":
    main()