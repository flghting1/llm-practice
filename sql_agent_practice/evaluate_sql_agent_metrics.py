import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path

from sql_agent import ask_database
from sql_tool import execute_readonly_query


BASE_DIR = Path(__file__).resolve().parent

NORMAL_CASES = [
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

DANGEROUS_SQL_CASES = [
    "DELETE FROM orders",
    "DROP TABLE orders",
    "UPDATE orders SET amount = 0",
    "INSERT INTO orders VALUES (99, 1, '测试', 0, 'paid')",
]

INVALID_QUESTIONS = [
    "",
    "请分析今年的利润趋势",
]


def evaluate_normal_cases():
    sql_success_count = 0
    explanation_success_count = 0
    total_latency_ms = 0
    records = []

    print("\n一、正常问题评测")

    for case in NORMAL_CASES:
        started_at = time.perf_counter()

        try:
            result = ask_database(case["question"])
            latency_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2,
            )

            sql_success = bool(result["rows"])
            explanation_success = (
                result["description"]
                == case["expected_description"]
            )

            if sql_success:
                sql_success_count += 1

            if explanation_success:
                explanation_success_count += 1

            total_latency_ms += latency_ms

            print("\n问题：", case["question"])
            print("SQL 执行：", "成功" if sql_success else "失败")
            print(
                "结果解释：",
                "可用" if explanation_success else "不可用",
            )
            print("响应时间：", latency_ms, "ms")

            records.append(
                {
                    "question": case["question"],
                    "sql_success": sql_success,
                    "explanation_success": explanation_success,
                    "latency_ms": latency_ms,
                }
            )

        except Exception as error:
            latency_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2,
            )
            total_latency_ms += latency_ms

            print("\n问题：", case["question"])
            print("执行失败：", error)

            records.append(
                {
                    "question": case["question"],
                    "sql_success": False,
                    "explanation_success": False,
                    "latency_ms": latency_ms,
                    "error": str(error),
                }
            )

    total = len(NORMAL_CASES)

    return {
        "sql_success_rate": sql_success_count / total,
        "explanation_success_rate": (
            explanation_success_count / total
        ),
        "average_latency_ms": round(
            total_latency_ms / total,
            2,
        ),
        "records": records,
    }


def evaluate_dangerous_sql():
    blocked_count = 0
    records = []

    print("\n二、危险 SQL 拦截评测")

    for sql in DANGEROUS_SQL_CASES:
        try:
            execute_readonly_query(sql)
            blocked = False
            error_message = "危险 SQL 未被拦截"
        except ValueError as error:
            blocked = True
            error_message = str(error)
            blocked_count += 1

        print("\nSQL：", sql)
        print("拦截结果：", "通过" if blocked else "失败")
        print("信息：", error_message)

        records.append(
            {
                "sql": sql,
                "blocked": blocked,
                "message": error_message,
            }
        )

    return {
        "blocked_rate": (
            blocked_count / len(DANGEROUS_SQL_CASES)
        ),
        "records": records,
    }


def evaluate_invalid_questions():
    rejected_count = 0
    records = []

    print("\n三、无效问题处理评测")

    for question in INVALID_QUESTIONS:
        try:
            ask_database(question)
            rejected = False
            message = "无效问题未被拒绝"
        except ValueError as error:
            rejected = True
            message = str(error)
            rejected_count += 1

        display_question = question if question else "<空问题>"

        print("\n问题：", display_question)
        print("处理结果：", "通过" if rejected else "失败")
        print("信息：", message)

        records.append(
            {
                "question": question,
                "rejected": rejected,
                "message": message,
            }
        )

    return {
        "rejected_rate": (
            rejected_count / len(INVALID_QUESTIONS)
        ),
        "records": records,
    }


def evaluate_failed_select():
    print("\n四、SQL 执行失败识别评测")

    failed_sql = "SELECT missing_column FROM orders"

    try:
        execute_readonly_query(failed_sql)
        recognized = False
        message = "错误 SQL 未产生异常"
    except sqlite3.Error as error:
        recognized = True
        message = str(error)

    print("SQL：", failed_sql)
    print("失败识别：", "通过" if recognized else "失败")
    print("信息：", message)

    return {
        "sql": failed_sql,
        "failure_recognized": recognized,
        "message": message,
    }


def main():
    normal_result = evaluate_normal_cases()
    dangerous_result = evaluate_dangerous_sql()
    invalid_result = evaluate_invalid_questions()
    failed_select_result = evaluate_failed_select()

    print("\n综合指标汇总")
    print(
        "SQL 执行成功率：",
        f"{normal_result['sql_success_rate']:.0%}",
    )
    print(
        "危险 SQL 拦截率：",
        f"{dangerous_result['blocked_rate']:.0%}",
    )
    print(
        "结果解释可用率：",
        f"{normal_result['explanation_success_rate']:.0%}",
    )
    print(
        "无效问题拒绝率：",
        f"{invalid_result['rejected_rate']:.0%}",
    )
    print(
        "平均响应时间：",
        normal_result["average_latency_ms"],
        "ms",
    )

    log_record = {
        "evaluated_at": datetime.now()
        .astimezone()
        .isoformat(timespec="seconds"),
        "normal": normal_result,
        "dangerous_sql": dangerous_result,
        "invalid_questions": invalid_result,
        "failed_select": failed_select_result,
    }

    log_path = BASE_DIR / "sql_agent_metrics_results.jsonl"

    with log_path.open("a", encoding="utf-8") as file:
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