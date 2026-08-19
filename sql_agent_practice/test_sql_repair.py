from sql_agent import execute_sql_with_one_repair


def main():
    repairable_sql = """
    SELECT product, SUM(total_price) AS total_amount
    FROM orders
    WHERE order_status = 'paid'
    GROUP BY product
    """

    repaired_result = execute_sql_with_one_repair(
        repairable_sql
    )

    assert repaired_result["repaired"] is True
    assert repaired_result["attempts"] == 2
    assert repaired_result["rows"]
    assert "total_price" not in repaired_result["sql"]
    assert "order_status" not in repaired_result["sql"]

    print("可修复 SQL：通过")
    print("执行次数：", repaired_result["attempts"])
    print("修复后 SQL：")
    print(repaired_result["sql"])
    print("查询结果：", repaired_result["rows"])

    unrepairable_sql = """
    SELECT total_price
    FROM missing_table
    """

    try:
        execute_sql_with_one_repair(unrepairable_sql)
        raise AssertionError("不可修复 SQL 不应执行成功")
    except RuntimeError as error:
        assert "已停止重试" in str(error)
        print("\n不可修复 SQL：通过")
        print(error)

    print("\nSQL 单次修复机制测试全部通过")


if __name__ == "__main__":
    main()