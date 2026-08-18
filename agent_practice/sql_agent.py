import json
from pathlib import Path
from datetime import datetime

from sql_tool import execute_read_only_sql


BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "database_schema.json"
LOG_PATH = BASE_DIR / "sql_tool_calls.jsonl"


TOP_PRODUCT_SQL = """
SELECT
    products.name AS product_name,
    ROUND(
        SUM(
            products.price
            * orders.quantity
        ),
        2
    ) AS sales
FROM orders
JOIN products
    ON orders.product_id = products.id
GROUP BY products.id, products.name
ORDER BY sales DESC
LIMIT 1
"""

PAID_USERS_SQL = """
SELECT COUNT(*) AS paid_user_count
FROM users
WHERE is_paid = 1
"""


CHANNEL_USERS_SQL = """
SELECT
    channel,
    COUNT(*) AS user_count
FROM users
GROUP BY channel
ORDER BY user_count DESC, channel
LIMIT 100
"""


def execute_logged_sql(
    query: str,
) -> dict:
    result = execute_read_only_sql(query)

    record = {
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
        "query": query,
        "result": result,
    }

    with LOG_PATH.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
        )

    return result


def load_schema() -> dict:
    text = SCHEMA_PATH.read_text(
        encoding="utf-8"
    )
    return json.loads(text)


def decide_sql(question: str) -> dict | None:
    if (
        "产品" in question
        and "销售额" in question
        and "最高" in question
    ):
        return {
            "report_type": "top_product",
            "tool": "read_only_sql",
            "arguments": {
                "query": TOP_PRODUCT_SQL,
            },
        }

    if "付费用户" in question:
        return {
            "report_type": "paid_users",
            "tool": "read_only_sql",
            "arguments": {
                "query": PAID_USERS_SQL,
            },
        }

    if (
        "渠道" in question
        and "用户" in question
    ):
        return {
            "report_type": "channel_users",
            "tool": "read_only_sql",
            "arguments": {
                "query": CHANNEL_USERS_SQL,
            },
        }

    return None


def run_sql_agent(question: str) -> dict:
    schema = load_schema()

    state = {
        "question": question,
        "schema_tables": list(
            schema["tables"].keys()
        ),
        "steps": [],
    }

    tool_call = decide_sql(question)

    if tool_call is None:
        return {
            "answer": "无法生成安全的查询。",
            "state": state,
        }

    state["steps"].append(
        {
            "type": "decision",
            "content": tool_call,
        }
    )

    tool_result = execute_logged_sql(
        tool_call["arguments"]["query"]
    )

    state["steps"].append(
        {
            "type": "observation",
            "content": tool_result,
        }
    )

    if tool_result["status"] == "error":
        answer = (
            "SQL 执行失败："
            + tool_result["error"]
        )
    elif not tool_result["rows"]:
        answer = "查询成功，但没有数据。"
    else:
        rows = tool_result["rows"]
        report_type = tool_call["report_type"]

    if report_type == "top_product":
        row = rows[0]
        answer = (
            f"销售额最高的产品是"
            f"《{row['product_name']}》，"
            f"销售额为 {row['sales']:.2f}。"
        )

    elif report_type == "paid_users":
        count = rows[0]["paid_user_count"]
        answer = f"付费用户共有 {count} 人。"

    else:
        channel_items = [
            f"{row['channel']}：{row['user_count']} 人"
            for row in rows
        ]
        answer = (
            "各渠道用户数："
            + "；".join(channel_items)
        )

    return {
        "answer": answer,
        "state": state,
    }


def main():
    questions = [
        "哪个产品销售额最高？",
        "付费用户有多少人？",
        "每个渠道有多少用户？",
        "请删除所有订单",
        "请显示数据库内部表",
        "帮我查询今天的天气",
    ]

    for question in questions:
        print("\n用户问题：", question)

        result = run_sql_agent(question)

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            )
        )
        print("=" * 50)


if __name__ == "__main__":
    main()