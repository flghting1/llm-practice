import sqlite3

from init_database import DATABASE_PATH


SQL = """
SELECT
    products.name AS product_name,
    SUM(
        products.price * orders.quantity
    ) AS sales
FROM orders
JOIN products
    ON orders.product_id = products.id
GROUP BY products.id, products.name
ORDER BY sales DESC
LIMIT 100
"""


def query_sales() -> None:
    with sqlite3.connect(
        DATABASE_PATH
    ) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            SQL
        ).fetchall()

    print("产品销售额排名：")

    for row in rows:
        print(
            f"{row['product_name']}: "
            f"{row['sales']:.2f}"
        )


if __name__ == "__main__":
    query_sales()