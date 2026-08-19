import json
import time
from datetime import datetime
from pathlib import Path

from sql_agent import ask_database


BASE_DIR = Path(__file__).resolve().parent

TEST_CASES = [
    {
        "question": "各商品的销售额是多少？",
        "expected_description": "统计各商品已支付订单的销售额",
    },
    {
        "question": "每个城市有多少客户？",
        "expected_description": "统计各城市的客户数量",
    },
    {
        "question": "不同状态的订单数量是多少？",
        "expected_description": "统计不同状态的订单数量",
    },
    {
        "question": "谁的消费最高？",
        "expected_description": "查询已支付订单消费金额最高的客户",
    },
]


def main():
    passed = 0
    total_latency_ms = 0
    case_records = []

    for case in TEST_CASES:
        print("\n问题：", case["question"])
        started_at = time.perf_counter()

        try:
            result = ask_database(case["question"])

            latency_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2,
            )
            description_correct = (
                result["description"]
                == case["expected_description"]
            )
            result_nonempty = bool(result["rows"])
            success = (
                description_correct
                and result_nonempty
            )

            if success:
                passed += 1

            print("生成说明：", result["description"])
            print("结果数量：", len(result["rows"]))
            print("响应时间：", latency_ms, "ms")
            print(
                "评测结果：",
                "通过" if success else "失败",
            )

            case_records.append(
                {
                    "question": case["question"],
                    "success": success,
                    "row_count": len(result["rows"]),
                    "latency_ms": latency_ms,
                }
            )
            total_latency_ms += latency_ms

        except ValueError as error:
            latency_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2,
            )
            print("错误：", error)
            print("响应时间：", latency_ms, "ms")
            print("评测结果：失败")

            case_records.append(
                {
                    "question": case["question"],
                    "success": False,
                    "error": str(error),
                    "latency_ms": latency_ms,
                }
            )
            total_latency_ms += latency_ms

    total = len(TEST_CASES)
    accuracy = passed / total
    average_latency_ms = round(
        total_latency_ms / total,
        2,
    )

    print("\n评测汇总")
    print("问题数量：", total)
    print("通过数量：", passed)
    print("SQL Agent 通过率：", f"{accuracy:.0%}")
    print("平均响应时间：", average_latency_ms, "ms")

    log_record = {
        "evaluated_at": datetime.now()
        .astimezone()
        .isoformat(timespec="seconds"),
        "total": total,
        "passed": passed,
        "accuracy": accuracy,
        "average_latency_ms": average_latency_ms,
        "cases": case_records,
    }

    log_path = BASE_DIR / "sql_evaluation_results.jsonl"

    with log_path.open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(
                log_record,
                ensure_ascii=False,
            ) + "\n"
        )

    print("评测日志：", log_path.name)


if __name__ == "__main__":
    main()