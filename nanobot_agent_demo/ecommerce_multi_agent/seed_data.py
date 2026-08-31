"""Creates a small local SQLite database used only by the portfolio demo."""

from __future__ import annotations

import sqlite3
from pathlib import Path


DATA_DIR = Path(__file__).parent / "data"
DATABASE_PATH = DATA_DIR / "ecommerce_demo.sqlite3"


def create_demo_database(database_path: Path = DATABASE_PATH) -> Path:
    """Create deterministic sample data; no real merchant or customer data is used."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    try:
        connection.executescript(
            """
            DROP TABLE IF EXISTS orders;
            DROP TABLE IF EXISTS inventory;
            DROP TABLE IF EXISTS products;

            CREATE TABLE products (
                sku TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                material TEXT NOT NULL,
                selling_points TEXT NOT NULL,
                price REAL NOT NULL
            );
            CREATE TABLE inventory (
                sku TEXT PRIMARY KEY,
                available_units INTEGER NOT NULL,
                safety_stock INTEGER NOT NULL,
                FOREIGN KEY (sku) REFERENCES products(sku)
            );
            CREATE TABLE orders (
                order_id TEXT PRIMARY KEY,
                order_date TEXT NOT NULL,
                sku TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                paid_amount REAL NOT NULL,
                channel TEXT NOT NULL,
                FOREIGN KEY (sku) REFERENCES products(sku)
            );
            """
        )
        connection.executemany(
            "INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("CB-001", "帆布通勤托特包", "通勤包", "12oz 帆布", "可装 A4；内置小口袋；磁吸开合", 79.0),
                ("BM-002", "不锈钢保温杯", "饮水杯", "304 不锈钢", "500ml；旋盖；适合日常通勤", 69.0),
                ("NB-003", "笔记本收纳包", "数码配件", "防泼水尼龙", "适配 13 英寸设备；前置收纳袋", 59.0),
            ],
        )
        connection.executemany(
            "INSERT INTO inventory VALUES (?, ?, ?)",
            [("CB-001", 8, 12), ("BM-002", 30, 15), ("NB-003", 4, 10)],
        )
        connection.executemany(
            "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("D-1001", "2026-08-30", "CB-001", 2, 158.0, "店铺自然流量"),
                ("D-1002", "2026-08-30", "BM-002", 1, 69.0, "店铺自然流量"),
                ("D-1003", "2026-08-30", "NB-003", 3, 177.0, "内容推荐"),
                ("D-1004", "2026-08-29", "CB-001", 1, 79.0, "内容推荐"),
            ],
        )
        connection.commit()
    finally:
        connection.close()
    return database_path
