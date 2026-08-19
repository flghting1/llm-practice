import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "sales.db"


def main():
    connection = sqlite3.connect(DATABASE_PATH)

    connection.executescript(
        """
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            registered_at TEXT NOT NULL
        );

        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            ordered_at TEXT NOT NULL,
            FOREIGN KEY (customer_id)
                REFERENCES customers (id)
        );

        INSERT INTO customers (
            id, name, city, registered_at
        ) VALUES
            (1, '张伟', '长沙', '2025-01-10'),
            (2, '李娜', '深圳', '2025-02-15'),
            (3, '王强', '长沙', '2025-03-20'),
            (4, '赵敏', '广州', '2025-04-05');

        INSERT INTO orders (
            id, customer_id, product, amount, status, ordered_at
        ) VALUES
            (1, 1, 'AI课程', 299.0, 'paid', '2025-05-01'),
            (2, 1, 'Python课程', 199.0, 'paid', '2025-05-03'),
            (3, 2, 'AI课程', 299.0, 'paid', '2025-05-05'),
            (4, 3, 'Docker课程', 159.0, 'refunded', '2025-05-08'),
            (5, 3, 'RAG课程', 399.0, 'paid', '2025-05-10'),
            (6, 4, 'Python课程', 199.0, 'paid', '2025-05-12');
        """
    )

    connection.commit()
    connection.close()

    print("数据库已创建：", DATABASE_PATH)
    print("数据表：customers, orders")


if __name__ == "__main__":
    main()