import json
import time
import urllib.request
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

SERVICES = [
    {
        "name": "RAG API",
        "health_url": "http://127.0.0.1:8001/health",
        "api_url": "http://127.0.0.1:8001/ask",
        "payload": {
            "question": "RAG 的完整流程是什么？",
        },
        "required_fields": {
            "answer",
            "sources",
        },
    },
    {
        "name": "SQL Agent API",
        "health_url": "http://127.0.0.1:8004/health",
        "api_url": "http://127.0.0.1:8004/ask",
        "payload": {
            "question": "各商品的销售额是多少？",
        },
        "required_fields": {
            "sql",
            "description",
            "rows",
        },
    },
    {
        "name": "Resume Matcher API",
        "health_url": "http://127.0.0.1:8006/health",
        "api_url": "http://127.0.0.1:8006/compare",
        "payload": {
            "resume_text": (
                "熟悉 Python、Git、FastAPI、RAG、"
                "Embedding、Docker、Streamlit、"
                "Prompt、Pydantic 和自动化测试。"
            ),
            "jd_items": [
                {
                    "name": "RAG 应用开发岗位",
                    "jd": (
                        "要求 Python、FastAPI、RAG、"
                        "Embedding、Docker、SQL 和测试经验。"
                    ),
                },
                {
                    "name": "后端 API 开发岗位",
                    "jd": (
                        "要求 Python、FastAPI、Git、"
                        "REST API 和 Docker。"
                    ),
                },
            ],
        },
        "required_fields": {
            "comparisons",
            "best_match",
            "recommendation",
        },
    },
]


def get_json(url: str) -> dict:
    with urllib.request.urlopen(
        url,
        timeout=30,
    ) as response:
        return json.load(response)


def post_json(url: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(
            payload,
            ensure_ascii=False,
        ).encode("utf-8"),
        headers={
            "Content-Type": (
                "application/json; charset=utf-8"
            )
        },
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=60,
    ) as response:
        return json.load(response)


def main():
    records = []
    passed = 0

    for service in SERVICES:
        print(f"\n服务：{service['name']}")
        started_at = time.perf_counter()

        try:
            health_result = get_json(
                service["health_url"]
            )
            health_passed = (
                health_result.get("ok") is True
            )

            api_result = post_json(
                service["api_url"],
                service["payload"],
            )

            fields_complete = (
                service["required_fields"].issubset(
                    api_result.keys()
                )
            )

            success = (
                health_passed
                and fields_complete
            )

            latency_ms = round(
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000,
                2,
            )

            if success:
                passed += 1

            print(
                "健康检查：",
                "通过" if health_passed else "失败",
            )
            print(
                "核心接口：",
                "通过" if fields_complete else "失败",
            )
            print("响应时间：", latency_ms, "ms")

            records.append(
                {
                    "service": service["name"],
                    "success": success,
                    "health_passed": health_passed,
                    "fields_complete": fields_complete,
                    "latency_ms": latency_ms,
                }
            )

        except Exception as error:
            latency_ms = round(
                (
                    time.perf_counter()
                    - started_at
                )
                * 1000,
                2,
            )

            print("验收结果：失败")
            print("错误：", error)

            records.append(
                {
                    "service": service["name"],
                    "success": False,
                    "latency_ms": latency_ms,
                    "error": str(error),
                }
            )

    total = len(SERVICES)
    success_rate = passed / total

    print("\n统一部署验收汇总")
    print("服务数量：", total)
    print("通过数量：", passed)
    print("部署验收通过率：", f"{success_rate:.0%}")

    log_record = {
        "verified_at": datetime.now()
        .astimezone()
        .isoformat(timespec="seconds"),
        "total": total,
        "passed": passed,
        "success_rate": success_rate,
        "services": records,
    }

    log_path = (
        BASE_DIR
        / "deployment_verification_results.jsonl"
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

    print("验收日志：", log_path.name)

    raise SystemExit(
        0 if passed == total else 1
    )


if __name__ == "__main__":
    main()