import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "sales.db"


USERS = [
    (1, "张三", "搜索", 1),
    (2, "李四", "短视频", 0),
    (3, "王五", "搜索", 1),
    (4, "赵六", "社交媒体", 0),
    (5, "陈七", "短视频", 1),
]

PRODUCTS = [
    (1, "Python 入门课", "课程", 199.0),
    (2, "FastAPI 实战课", "课程", 299.0),
    (3, "RAG 项目课", "课程", 399.0),
    (4, "求职辅导", "服务", 599.0),
]

ORDERS = [
    (1, 1, 1, 1, "2026-08-01"),
    (2, 1, 3, 1, "2026-08-03"),
    (3, 2, 1, 2, "2026-08-04"),
    (4, 3, 2, 1, "2026-08-05"),
    (5, 3, 4, 1, "2026-08-06"),
    (6, 4, 1, 1, "2026-08-07"),
    (7, 5, 3, 2, "2026-08-08"),
    (8, 5, 2, 1, "2026-08-09"),
]


def create_database() -> None:
    with sqlite3.connect(
        DATABASE_PATH
    ) as connection:
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                channel TEXT NOT NULL,
                is_paid INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                order_date TEXT NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES users (id),
                FOREIGN KEY (product_id)
                    REFERENCES products (id)
            );
            """
        )

        connection.executemany(
            """
            INSERT OR REPLACE INTO users
            (id, name, channel, is_paid)
            VALUES (?, ?, ?, ?)
            """,
            USERS,
        )

        connection.executemany(
            """
            INSERT OR REPLACE INTO products
            (id, name, category, price)
            VALUES (?, ?, ?, ?)
            """,
            PRODUCTS,
        )

        connection.executemany(
            """
            INSERT OR REPLACE INTO orders
            (
                id,
                user_id,
                product_id,
                quantity,
                order_date
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            ORDERS,
        )

        user_count = connection.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        product_count = connection.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]

        order_count = connection.execute(
            "SELECT COUNT(*) FROM orders"
        ).fetchone()[0]

    print("数据库位置：", DATABASE_PATH)
    print("用户数量：", user_count)
    print("产品数量：", product_count)
    print("订单数量：", order_count)


if __name__ == "__main__":
    create_database()