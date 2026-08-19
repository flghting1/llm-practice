from sql_agent import ask_database
from sql_tool import execute_readonly_query


def expect_error(label, function, value):
    try:
        function(value)
    except ValueError as error:
        print(f"{label}：已拦截")
        print("原因：", error)
    else:
        print(f"{label}：失败，危险输入未被拦截")


def main():
    print("测试 1：空问题")

    expect_error(
        "空问题",
        ask_database,
        "",
    )

    print("\n测试 2：未知问题")

    expect_error(
        "未知问题",
        ask_database,
        "明天天气怎么样？",
    )

    print("\n测试 3：直接执行 DELETE")

    expect_error(
        "DELETE",
        execute_readonly_query,
        "DELETE FROM orders",
    )

    print("\n测试 4：直接执行 DROP")

    expect_error(
        "DROP",
        execute_readonly_query,
        "DROP TABLE orders",
    )


if __name__ == "__main__":
    main()