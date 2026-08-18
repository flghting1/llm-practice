import json
import sqlite3
from datetime import datetime

from init_database import DATABASE_PATH


MAX_ROWS = 100
ALLOWED_TABLES = {
    "users",
    "products",
    "orders",
}


def authorize_database_access(
    action_code: int,
    argument_one: str | None,
    argument_two: str | None,
    database_name: str | None,
    trigger_name: str | None,
) -> int:
    if action_code == sqlite3.SQLITE_READ:
        table_name = argument_one

        if table_name not in ALLOWED_TABLES:
            return sqlite3.SQLITE_DENY

    return sqlite3.SQLITE_OK


def execute_read_only_sql(
    query: str,
) -> dict:
    normalized_query = query.strip()

    if not normalized_query:
        return {
            "status": "error",
            "error": "SQL 不能为空",
        }

    first_word = normalized_query.split(
    None,
    1,
    )[0].upper()

    if first_word != "SELECT":
        return {
            "status": "error",
            "error": "只允许执行 SELECT",
        }

    normalized_query = normalized_query.rstrip(
        ";"
    )

    if ";" in normalized_query:
        return {
            "status": "error",
            "error": "只允许执行一条 SQL",
        }

    print(
        "[SQL 工具日志]",
        datetime.now().isoformat(
            timespec="seconds"
        ),
        normalized_query,
    )

    limited_query = (
        "SELECT * FROM ("
        + normalized_query
        + f") LIMIT {MAX_ROWS + 1}"
    )

    database_uri = (
        DATABASE_PATH.as_uri()
        + "?mode=ro"
    )

    try:
        with sqlite3.connect(
            database_uri,
            uri=True,
        ) as connection:
            connection.set_authorizer(
    authorize_database_access
)
            connection.row_factory = sqlite3.Row

            rows = connection.execute(
                limited_query
            ).fetchall()

    except sqlite3.Error as error:
        return {
            "status": "error",
            "error": str(error),
        }

    truncated = len(rows) > MAX_ROWS
    rows = rows[:MAX_ROWS]

    return {
        "status": "success",
        "row_count": len(rows),
        "truncated": truncated,
        "rows": [
            dict(row)
            for row in rows
        ],
    }


def main():
    queries = [
    "SELECT COUNT(*) AS count FROM orders",
    "SELECT name FROM sqlite_master",
    (
        "SELECT * FROM users; "
        "DELETE FROM orders"
    ),
]

    for query in queries:
        print("\nSQL：", query)

        result = execute_read_only_sql(query)

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