from fastapi.testclient import TestClient

from resume_api import app


client = TestClient(app)


RESUME_TEXT = """
熟悉 Python、Git、FastAPI、RAG、Embedding、Docker、
Streamlit、Prompt、Pydantic 和自动化测试。
"""

JD_TEXT = """
岗位要求：Python、FastAPI、RAG、Embedding、Docker、
SQL、Streamlit 和测试经验。
"""


def main():
    health_response = client.get("/health")

    assert health_response.status_code == 200
    assert health_response.json()["ok"] is True
    print("健康检查：通过")

    match_response = client.post(
        "/match",
        json={
            "resume_text": RESUME_TEXT,
            "jd_text": JD_TEXT,
        },
    )

    assert match_response.status_code == 200

    result = match_response.json()

    assert "matched_skills" in result
    assert "missing_skills" in result
    assert "projects_to_build" in result
    assert "risk_level" in result
    assert "match_score" in result

    assert "SQL" in result["missing_skills"]
    assert result["match_score"] == 88

    print("匹配接口：通过")
    print("匹配分数：", result["match_score"])
    print("缺少技能：", result["missing_skills"])

    empty_response = client.post(
        "/match",
        json={
            "resume_text": "",
            "jd_text": JD_TEXT,
        },
    )

    assert empty_response.status_code == 422
    print("空简历校验：通过")

    print("\nFastAPI 接口测试全部通过")


if __name__ == "__main__":
    main()