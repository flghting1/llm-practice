import sqlite3

from sql_tool import execute_readonly_query


QUESTION_RULES = [
    {
        "keywords": ["销售额", "商品"],
        "sql": """
        SELECT
            product,
            SUM(amount) AS total_amount
        FROM orders
        WHERE status = 'paid'
        GROUP BY product
        ORDER BY total_amount DESC
        """,
        "description": "统计各商品已支付订单的销售额",
    },
    {
        "keywords": ["城市", "客户"],
        "sql": """
        SELECT
            city,
            COUNT(*) AS customer_count
        FROM customers
        GROUP BY city
        ORDER BY customer_count DESC
        """,
        "description": "统计各城市的客户数量",
    },
    {
        "keywords": ["订单", "数量"],
        "sql": """
        SELECT
            status,
            COUNT(*) AS order_count
        FROM orders
        GROUP BY status
        ORDER BY order_count DESC
        """,
        "description": "统计不同状态的订单数量",
    },
    {
        "keywords": ["最高", "消费"],
        "sql": """
        SELECT
            customers.name,
            SUM(orders.amount) AS total_amount
        FROM customers
        JOIN orders
            ON customers.id = orders.customer_id
        WHERE orders.status = 'paid'
        GROUP BY customers.id, customers.name
        ORDER BY total_amount DESC
        LIMIT 1
        """,
        "description": "查询已支付订单消费金额最高的客户",
    },
]

COMMON_COLUMN_REPAIRS = {
    "total_price": "amount",
    "order_status": "status",
    "product_name": "product",
}


def generate_sql(question: str) -> dict:
    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("问题不能为空")

    for rule in QUESTION_RULES:
        if all(
            keyword in cleaned_question
            for keyword in rule["keywords"]
        ):
            return {
                "sql": rule["sql"].strip(),
                "description": rule["description"],
            }

    raise ValueError("暂时无法把这个问题转换为 SQL")


def repair_sql_once(sql: str) -> str:
    repaired_sql = sql

    for wrong_name, correct_name in COMMON_COLUMN_REPAIRS.items():
        repaired_sql = repaired_sql.replace(
            wrong_name,
            correct_name,
        )

    if repaired_sql == sql:
        raise RuntimeError("没有匹配到可用的 SQL 修复规则")

    return repaired_sql


def execute_sql_with_one_repair(sql: str) -> dict:
    try:
        rows = execute_readonly_query(sql)

        return {
            "sql": sql,
            "rows": rows,
            "repaired": False,
            "attempts": 1,
            "original_error": None,
        }

    except sqlite3.Error as first_error:
        repaired_sql = repair_sql_once(sql)

        try:
            rows = execute_readonly_query(repaired_sql)
        except (sqlite3.Error, ValueError) as second_error:
            raise RuntimeError(
                "SQL 修复一次后仍执行失败，已停止重试："
                f"{second_error}"
            ) from second_error

        return {
            "sql": repaired_sql,
            "rows": rows,
            "repaired": True,
            "attempts": 2,
            "original_error": str(first_error),
        }


def ask_database(question: str) -> dict:
    generated = generate_sql(question)
    execution = execute_sql_with_one_repair(generated["sql"])

    return {
        "question": question,
        "sql": execution["sql"],
        "description": generated["description"],
        "rows": execution["rows"],
        "repaired": execution["repaired"],
        "attempts": execution["attempts"],
        "original_error": execution["original_error"],
    }


def main():
    question = "各商品的销售额是多少？"
    result = ask_database(question)

    print("用户问题：")
    print(result["question"])

    print("\n生成 SQL：")
    print(result["sql"])

    print("\n查询说明：")
    print(result["description"])

    print("\n执行次数：")
    print(result["attempts"])

    print("\n查询结果：")

    for row in result["rows"]:
        print(row)


if __name__ == "__main__":
    main()