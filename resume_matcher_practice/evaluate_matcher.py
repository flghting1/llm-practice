import json
from datetime import datetime
from pathlib import Path

from matcher import match_resume_to_jd


BASE_DIR = Path(__file__).resolve().parent
RESUME_TEXT = """
熟悉 Python、Git、FastAPI、RAG、Embedding、Docker、
Streamlit、Prompt、Pydantic 和自动化测试。
"""


def main():
    cases_path = BASE_DIR / "jd_cases.json"

    with cases_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

    passed = 0
    records = []

    for case in cases:
        report = match_resume_to_jd(
            RESUME_TEXT,
            case["jd"],
        )

        actual_missing = report.missing_skills
        expected_missing = sorted(
            case["expected_missing"]
        )

        missing_correct = (
            actual_missing == expected_missing
        )

        if missing_correct:
            passed += 1

        print("\n岗位：", case["name"])
        print("匹配分数：", report.match_score)
        print("已掌握技能：", report.matched_skills)
        print("缺少技能：", actual_missing)
        print(
            "评测结果：",
            "通过" if missing_correct else "失败",
        )

        records.append(
            {
                "name": case["name"],
                "match_score": report.match_score,
                "missing_skills": actual_missing,
                "expected_missing": expected_missing,
                "missing_correct": missing_correct,
                "risk_level": report.risk_level,
            }
        )

    total = len(cases)
    accuracy = passed / total

    print("\n评测汇总")
    print("岗位数量：", total)
    print("通过数量：", passed)
    print("缺口识别准确率：", f"{accuracy:.0%}")

    log_path = BASE_DIR / "matcher_evaluation_results.jsonl"

    log_record = {
        "evaluated_at": datetime.now()
        .astimezone()
        .isoformat(timespec="seconds"),
        "total": total,
        "passed": passed,
        "accuracy": accuracy,
        "cases": records,
    }

    with log_path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                log_record,
                ensure_ascii=False,
            )
            + "\n"
        )

    print("评测日志：", log_path.name)


if __name__ == "__main__":
    main()