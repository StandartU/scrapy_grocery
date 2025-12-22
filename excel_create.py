import os
import sqlite3
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_FILE = os.path.join(BASE_DIR, "application", "products.db")

SITE_NAME = "yarcheplus"
DATE_STR = datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
OUTPUT_FILE = os.path.join(REPORT_DIR, f"{SITE_NAME}_{DATE_STR}.xlsx")

QUERY = """
WITH ranked AS (
    SELECT
        *,
        LAG(price_regular) OVER (
            PARTITION BY article
            ORDER BY date_scraped ASC
        ) AS previous_price
    FROM products
)
SELECT
    product_url            AS "Ссылка",
    category_url           AS "Категория",
    article                AS "Артикул",
    name                   AS "Название",
    images_url             AS "Картинки",
    previous_price         AS "Прошлая цена",
    price_regular          AS "Текущая цена",
    price_discount         AS "Цена со скидкой",
    description            AS "Описание",
    characteristics        AS "Характеристики",
    compound               AS "Состав",
    rating                 AS "Рейтинг",
    reviews_count          AS "Кол-во отзывов",
    reviews                AS "Отзывы",
    date_scraped           AS "Дата сбора"
FROM ranked
WHERE previous_price IS NOT NULL
  AND price_regular < previous_price
ORDER BY article, date_scraped DESC;
"""

def main():
    if not os.path.exists(DB_FILE):
        print("База данных не инициализирована или удалена")
        return

    conn = sqlite3.connect(DB_FILE)

    df = pd.read_sql_query(QUERY, conn)
    conn.close()

    if df.empty:
        print("Нет товаров с понижением цены")
        return

    if not os.path.exists(REPORT_DIR):
        os.mkdir(REPORT_DIR)

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Excel создан: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
