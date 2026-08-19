import json
from datetime import datetime
from pathlib import Path

from match_schema import MatchReport
from matcher import match_resume_to_jd


BASE_DIR = Path(__file__).resolve().parent

RESUME_TEXT = """
熟悉 Python、Git、FastAPI、RAG、Embedding、Docker、
Streamlit、Prompt、Pydantic 和自动化测试。
"""

REQUIRED_FIELDS = {
    "matched_skills",
    "missing_skills",
    "projects_to_build",
    "risk_level",
    "match_score",
    "explanation",
    "interview_risks",
}


def suggestion_is_actionable(report: MatchReport) -> bool:
    if not report.missing_skills:
        return True

    suggestions = " ".join(
        report.projects_to_build
    ).lower()

    return all(
        skill.lower() in suggestions
        for skill in report.missing_skills
    )


def main():
    cases_path = BASE_DIR / "jd_cases.json"

    with cases_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

    json_valid_count = 0
    complete_count = 0
    stable_count = 0
    actionable_count = 0
    records = []

    for case in cases:
        reports = [
            match_resume_to_jd(
                RESUME_TEXT,
                case["jd"],
            )
            for _ in range(3)
        ]

        first_report = reports[0]
        output_json = first_report.model_dump_json(
            ensure_ascii=False
        )

        try:
            parsed_output = json.loads(output_json)
            MatchReport.model_validate(parsed_output)
            json_valid = True
            json_valid_count += 1
        except (json.JSONDecodeError, ValueError):
            parsed_output = {}
            json_valid = False

        fields_complete = (
            REQUIRED_FIELDS.issubset(
                parsed_output.keys()
            )
        )

        if fields_complete:
            complete_count += 1

        serialized_reports = [
            report.model_dump_json(
                ensure_ascii=False
            )
            for report in reports
        ]

        stable = len(set(serialized_reports)) == 1

        if stable:
            stable_count += 1

        actionable = suggestion_is_actionable(
            first_report
        )

        if actionable:
            actionable_count += 1

        print("\n岗位：", case["name"])
        print(
            "JSON 合法：",
            "通过" if json_valid else "失败",
        )
        print(
            "字段完整：",
            "通过" if fields_complete else "失败",
        )
        print(
            "连续三次输出稳定：",
            "通过" if stable else "失败",
        )
        print(
            "建议可执行：",
            "通过" if actionable else "失败",
        )

        records.append(
            {
                "name": case["name"],
                "json_valid": json_valid,
                "fields_complete": fields_complete,
                "stable": stable,
                "actionable": actionable,
            }
        )

    total = len(cases)

    metrics = {
        "json_valid_rate": json_valid_count / total,
        "field_completeness_rate": complete_count / total,
        "stability_rate": stable_count / total,
        "actionable_suggestion_rate": (
            actionable_count / total
        ),
    }

    print("\n输出质量评测汇总")
    print(
        "JSON 合法率：",
        f"{metrics['json_valid_rate']:.0%}",
    )
    print(
        "字段完整率：",
        f"{metrics['field_completeness_rate']:.0%}",
    )
    print(
        "同一 JD 输出稳定率：",
        f"{metrics['stability_rate']:.0%}",
    )
    print(
        "建议可执行率：",
        f"{metrics['actionable_suggestion_rate']:.0%}",
    )

    log_record = {
        "evaluated_at": datetime.now()
        .astimezone()
        .isoformat(timespec="seconds"),
        "metrics": metrics,
        "cases": records,
    }

    log_path = (
        BASE_DIR
        / "output_quality_results.jsonl"
    )

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