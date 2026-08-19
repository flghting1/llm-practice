import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "sales.db"

FORBIDDEN_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "replace",
    "truncate",
    "attach",
    "detach",
    "pragma",
}

ALLOWED_SCHEMA = {
    "customers": {
        "id",
        "name",
        "city",
    },
    "orders": {
        "id",
        "customer_id",
        "product",
        "amount",
        "status",
    },
}


def validate_sql(sql: str) -> str:
    cleaned_sql = sql.strip()

    if not cleaned_sql:
        raise ValueError("SQL 不能为空")

    normalized_sql = cleaned_sql.lower()

    if not normalized_sql.startswith("select"):
        raise ValueError("只允许执行 SELECT 查询")

    if ";" in cleaned_sql.rstrip(";"):
        raise ValueError("只允许执行一条 SQL")

    words = normalized_sql.replace(";", " ").split()

    if FORBIDDEN_KEYWORDS.intersection(words):
        raise ValueError("SQL 包含禁止的关键字")

    return cleaned_sql.rstrip(";")


def create_authorizer(denied_access: list[str]):
    def authorize(
        action_code,
        table_name,
        column_name,
        database_name,
        trigger_name,
    ):
        if action_code != sqlite3.SQLITE_READ:
            return sqlite3.SQLITE_OK

        normalized_table = (table_name or "").lower()
        normalized_column = (column_name or "").lower()

        allowed_columns = ALLOWED_SCHEMA.get(normalized_table)

        if allowed_columns is None:
            denied_access.append(
                f"未授权表：{table_name}"
            )
            return sqlite3.SQLITE_DENY

        if (
            normalized_column
            and normalized_column not in allowed_columns
        ):
            denied_access.append(
                f"未授权字段：{table_name}.{column_name}"
            )
            return sqlite3.SQLITE_DENY

        return sqlite3.SQLITE_OK

    return authorize


def execute_readonly_query(sql: str) -> list[dict]:
    safe_sql = validate_sql(sql)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    denied_access = []
    connection.set_authorizer(
        create_authorizer(denied_access)
    )

    try:
        cursor = connection.execute(safe_sql)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    except sqlite3.DatabaseError as error:
        if denied_access:
            raise ValueError(
                "SQL 访问权限检查失败："
                + denied_access[0]
            ) from error

        raise

    finally:
        connection.close()


def main():
    sql = """
    SELECT
        product,
        SUM(amount) AS total_amount
    FROM orders
    WHERE status = 'paid'
    GROUP BY product
    ORDER BY total_amount DESC
    """

    results = execute_readonly_query(sql)

    print("执行 SQL：")
    print(sql.strip())
    print("\n查询结果：")

    for result in results:
        print(result)


if __name__ == "__main__":
    main()