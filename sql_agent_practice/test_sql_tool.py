from sql_tool import execute_readonly_query


def main():
    print("测试 1：正常 SELECT")

    results = execute_readonly_query(
        "SELECT COUNT(*) AS count FROM orders"
    )
    print(results)

    print("\n测试 2：危险 DELETE")

    try:
        execute_readonly_query("DELETE FROM orders")
    except ValueError as error:
        print("已拦截：", error)

    print("\n测试 3：多条 SQL")

    try:
        execute_readonly_query(
            "SELECT * FROM orders; DROP TABLE orders"
        )
    except ValueError as error:
        print("已拦截：", error)

    print("\n测试 4：结果行数上限")
    limited_results = execute_readonly_query(
        """
        SELECT first_order.id AS first_id
        FROM orders AS first_order
        CROSS JOIN orders AS second_order
        CROSS JOIN orders AS third_order
        """
    )
    assert len(limited_results) == 100
    print("结果已限制为：", len(limited_results))


if __name__ == "__main__":
    main()
