# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import os
import sqlite3
import json
from datetime import datetime
from scrapy.exceptions import DropItem

DB_FILENAME = "products.sqlite"


class SQLitePipeline:

    def __init__(self):
        self.conn = sqlite3.connect(DB_FILENAME)
        self.cur = self.conn.cursor()
        self._create_tables()


    def _create_tables(self):
        exists = os.path.exists(DB_FILENAME)
        if exists:
            return
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_url TEXT PRIMARY KEY,
                sku TEXT,
                name TEXT,
                category TEXT,
                images_json TEXT,
                description TEXT,
                attributes_json TEXT,
                ingredients TEXT,
                rating REAL,
                reviews_count INTEGER,
                reviews_json TEXT,
                last_seen TEXT
            )
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_url TEXT,
                price_regular REAL,
                price_discount REAL,
                date_scraped TEXT,
                FOREIGN KEY(product_url) REFERENCES products(product_url)
            )
        """)
        self.conn.commit()

    def process_item(self, item):

        if not item.get('product_url'):
            raise DropItem("Missing product_url")

        images_json = json.dumps(item.get('images') or [])
        attributes_json = json.dumps(item.get('attributes') or {})
        reviews_json = json.dumps(item.get('reviews') or [])

        now = item.get('date_scraped') or datetime.utcnow().isoformat() + "Z"

        self.cur.execute("""
            INSERT INTO products(product_url, sku, name, category, images_json, description, attributes_json, ingredients, rating, reviews_count, reviews_json, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(product_url) DO UPDATE SET
              sku=excluded.sku,
              name=excluded.name,
              category=excluded.category,
              images_json=excluded.images_json,
              description=excluded.description,
              attributes_json=excluded.attributes_json,
              ingredients=excluded.ingredients,
              rating=excluded.rating,
              reviews_count=excluded.reviews_count,
              reviews_json=excluded.reviews_json,
              last_seen=excluded.last_seen
        """, (
            item.get('product_url'),
            item.get('sku'),
            item.get('name'),
            item.get('category'),
            images_json,
            item.get('description'),
            attributes_json,
            item.get('ingredients'),
            item.get('rating'),
            item.get('reviews_count'),
            reviews_json,
            now
        ))

        self.cur.execute("""
            INSERT INTO prices(product_url, price_regular, price_discount, date_scraped)
            VALUES (?, ?, ?, ?)
        """, (
            item.get('product_url'),
            item.get('price_regular'),
            item.get('price_discount'),
            now
        ))

        self.conn.commit()
        return item
