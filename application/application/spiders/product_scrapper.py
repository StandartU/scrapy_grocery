import scrapy
import re
import json
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
        categories = response.css('a.aJjLH4KAr::attr(href)').getall()

        for category_url in categories:
            yield response.follow(
                category_url,
                callback=self.parse_category,
                cb_kwargs={"category_url": category_url}
            )

    def parse_category(self, response, category_url):
        product_urls = response.css('.aUuHgqUxc a::attr(href)').getall()

        for product_url in product_urls:
            product_id = extract_id(product_url)

            yield response.follow(
                product_url,
                callback=self.parse_product,
                cb_kwargs={
                    "product_id": product_id,
                    "product_url": product_url,
                    "category_url": category_url
                }
            )

        pagination_container = response.xpath('//div[contains(@class, "aft")]')

        if pagination_container:
            pages = pagination_container.xpath('.//a/@href').getall()

            for page in pages:
                yield response.follow(
                    page,
                    callback=self.parse_category,
                    cb_kwargs={"category_url": category_url}
                )

    def parse_product(self, response, product_id, product_url, category_url):
        payload = p.get_product_payload(product_id)

        yield scrapy.Request(
            url="https://api.yarcheplus.ru/api/graphql",
            method="POST",
            body=json.dumps(payload),
            callback=self.parse_product_reviews,
            headers={
                "Content-Type": "application/json"
            },
            cb_kwargs = {
                "product_id": product_id,
                "product_url": product_url,
                "category_url": category_url
            }
        )

    def parse_product_reviews(self, response, product_id, product_url, category_url):
        payload = p.get_review_payload(product_id)

        yield scrapy.Request(
            url="https://api.yarcheplus.ru/api/graphql",
            method="POST",
            body=json.dumps(payload),
            callback=self.save_product_data,
            headers={
                "Content-Type": "application/json"
            },
            cb_kwargs = {
                "product_id": product_id,
                "product_url": product_url,
                "category_url": category_url,
                "product_data": response.json()
            }
        )

    def save_product_data(self, response, product_id, product_url, category_url, product_data):
        item = ProductItem()
        data = product_data['data']['product']

        item['product_url'] = 'https://yarcheplus.ru{}'.format(product_url)
        item['category_url'] = 'https://yarcheplus.ru{}'.format(category_url)
        item['article'] = product_id
        item['name'] = data.get('name')

        images = data.get('images', [])
        item['images_url'] = [f"https://api.yarcheplus.ru/thumbnail/768x768/0/0/{img['id']}.png" for img in images]

        if data.get('previousPrice') is not None:
            item['price_regular'] = data.get('previousPrice')
            item['price_discount'] = data.get('price')
        else:
            item['price_regular'] = data.get('price')
            item['price_discount'] = None

        item['description'] = data.get('description')

        characteristics = {}
        compound = None
        for p in data.get('propertyValues', []):
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

        item['rating'] = data.get('rating')


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
