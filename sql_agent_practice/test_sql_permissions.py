from sql_tool import execute_readonly_query


def expect_blocked(label: str, sql: str):
    try:
        execute_readonly_query(sql)
    except ValueError as error:
        print(f"{label}：通过")
        print("原因：", error)
    else:
        raise AssertionError(
            f"{label}失败：未授权查询没有被拦截"
        )


def main():
    allowed_rows = execute_readonly_query(
        """
        SELECT product, amount, status
        FROM orders
        """
    )

    assert allowed_rows
    print("授权表和字段查询：通过")
    print("结果数量：", len(allowed_rows))

    expect_blocked(
        "未授权系统表",
        "SELECT name FROM sqlite_master",
    )

    expect_blocked(
        "未授权客户字段",
        "SELECT registered_at FROM customers",
    )

    expect_blocked(
        "未授权订单字段",
        "SELECT ordered_at FROM orders",
    )

    print("\nSQL 表和字段权限测试全部通过")


if __name__ == "__main__":
    main()