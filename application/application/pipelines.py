# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import sqlite3
import json
from datetime import datetime


class ProductPipelineSQLite:
    DB_FILE = 'products.db'
    TABLE_NAME = 'products'

    def open_spider(self, spider):
        self.conn = sqlite3.connect(self.DB_FILE)
        self.cursor = self.conn.cursor()

        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_url TEXT,
                category_url TEXT,
                article TEXT,
                name TEXT,
                images_url TEXT,
                price_regular REAL,
                price_discount REAL,
                description TEXT,
                characteristics TEXT,
                compound TEXT,
                rating REAL,
                reviews_count INTEGER,
                reviews TEXT,
                date_scraped TEXT
            )
        ''')
        self.conn.commit()

    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def process_item(self, item, spider):
        item['date_scraped'] = datetime.now().isoformat()

        self.cursor.execute(f'''
            INSERT INTO {self.TABLE_NAME} (
                product_url,
                category_url,
                article,
                name,
                images_url,
                price_regular,
                price_discount,
                description,
                characteristics,
                compound,
                rating,
                reviews_count,
                reviews,
                date_scraped
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.get('product_url'),
            item.get('category_url'),
            item.get('article'),
            item.get('name'),

            ','.join(item.get('images_url', [])) if item.get('images_url') else None,

            item.get('price_regular'),
            item.get('price_discount'),
            item.get('description'),

            json.dumps(
                item.get('characteristics', {}),
                ensure_ascii=False
            ),

            item.get('compound'),

            item.get('rating'),
            item.get('reviews_count'),

            json.dumps(
                item.get('reviews', []),
                ensure_ascii=False
            ),

            item.get('date_scraped')
        ))

        self.conn.commit()
        return item

