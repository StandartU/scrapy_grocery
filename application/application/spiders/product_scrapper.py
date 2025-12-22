import scrapy
import re
import json
import math
from datetime import datetime
from fake_useragent import UserAgent

from ..items import ProductItem
from ..ql import payload as p


class ProductSpider(scrapy.Spider):
    name = "product_scrapper"
    allowed_domains = ["yarcheplus.ru"]
    start_urls = ["https://yarcheplus.ru/"]
    
    custom_settings = {
        "User-Agent": UserAgent().firefox
    }

    def parse(self, response, **kwargs):
        # categories = response.css('a.aJjLH4KAr::attr(href)').getall()

        categories = response.xpath("//a[contains(@class, 'aJjLH4KAr') and contains(@class, 'a2XpkLhVn') and contains(@class, 'cJjLH4KAr')]/@href").getall()

        print(categories)

        for category_url in categories:
            category_id = extract_id(category_url)
            payload = p.get_category_payload(category_id, page=1, limit=100)

            yield scrapy.Request(
                url="https://api.yarcheplus.ru/api/graphql",
                method="POST",
                headers={"Content-Type": "application/json"},
                body=json.dumps(payload),
                callback=self.parse_category,
                cb_kwargs={"category_id": category_id,
                           "category_url": category_url,
                           "page": 1},
                dont_filter=True
            )


    def parse_category(self, response, category_url, category_id, page):
        data = response.json()["data"]["products"]
        total = data["page"]["total"]
        limit = data["page"]["limit"]
        total_pages = math.ceil(total / limit)
        product_ids = [item["id"] for item in data["list"]]

        self.logger.info(
            f"Parsing page {page} of {total_pages}. URL - {category_url}"
        )

        for product_id in product_ids:
            self.logger.debug(f"Yielding product_id: {product_id}")
            payload = p.get_product_payload(product_id)

            yield scrapy.Request(
                url="https://api.yarcheplus.ru/api/graphql",
                method="POST",
                headers={"Content-Type": "application/json"},
                body=json.dumps(payload),
                callback=self.parse_product,
                cb_kwargs={"product_id": product_id,
                           "category_url": category_url},
                dont_filter=True
            )

        if page == 1:
            for next_page in range(2, total_pages + 1):
                payload = p.get_category_payload(category_id, page=next_page, limit=limit)

                yield scrapy.Request(
                    url="https://api.yarcheplus.ru/api/graphql",
                    method="POST",
                    headers={"Content-Type": "application/json"},
                    body=json.dumps(payload),
                    callback=self.parse_category,
                    cb_kwargs={
                        "category_id": category_id,
                        "category_url": category_url,
                        "page": next_page
                    },
                dont_filter=True
                )


    def parse_product(self, response, product_id, category_url):
        payload = p.get_product_payload(product_id)

        self.logger.debug("parse_product: {}".format(product_id))

        yield scrapy.Request(
            url="https://api.yarcheplus.ru/api/graphql",
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps(payload),
            callback=self.parse_product_reviews,
            cb_kwargs={"category_url": category_url},
            dont_filter=True
        )

    def parse_product_reviews(self, response, category_url):
        data = response.json()["data"]["product"]

        product_code, product_id = data["code"], data["id"]

        self.logger.debug("parse_product_reviews: {}".format(product_id))

        product_url = "{}-{}".format(product_code, product_id)

        payload = p.get_review_payload(product_id)

        yield scrapy.Request(
            url="https://api.yarcheplus.ru/api/graphql",
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps(payload),
            callback=self.save_product_data,
            cb_kwargs={
                "product_id": product_id,
                "product_url": product_url,
                "category_url": category_url,
                "product_data": data
            },
            dont_filter=True
        )

    def save_product_data(self, response, product_id, product_url, category_url, product_data):
        item = ProductItem()

        item['product_url'] = 'https://yarcheplus.ru{}'.format(product_url)
        item['category_url'] = 'https://yarcheplus.ru{}'.format(category_url)
        item['article'] = product_id
        item['name'] = product_data.get('name')

        images = product_data.get('images', [])
        item['images_url'] = [f"https://api.yarcheplus.ru/thumbnail/768x768/0/0/{img['id']}.png" for img in images]

        if product_data.get('previousPrice') is not None:
            item['price_regular'] = product_data.get('previousPrice')
            item['price_discount'] = product_data.get('price')
        else:
            item['price_regular'] = product_data.get('price')
            item['price_discount'] = None

        item['description'] = product_data.get('description')

        characteristics = {}
        compound = None
        for p in product_data.get('propertyValues', []):
            title = p['property']['title']
            name = p['property']['name']

            if 'strValue' in p and p['strValue']:
                value = p['strValue']
            elif 'item' in p and p['item']:
                value = p['item']['label']
            else:
                value = None

            if name == 'composition':
                compound = value
            else:
                characteristics[title] = value

        item['characteristics'] = characteristics
        item['compound'] = compound

        item['rating'] = product_data.get('rating')

        review_data = response.json()['data']['productReviews']
        item['reviews'] = [
            {
                "author": r.get('author'),
                "date": r.get('dateCreated'),
                "rating": r.get('grade'),
                "text": r.get('text')
            }
            for r in review_data.get('list', [])
        ]

        item['reviews_count'] = len(item['reviews'])

        item['date_scraped'] = datetime.now().isoformat()

        yield item


def extract_id(url):
    match = re.search(r'-([0-9]+)(?:\?|$)', url)
    return match.group(1) if match else None