import scrapy
import re
import json
from fake_useragent import UserAgent
from ql import input as i
from ql import query as q


class ProductSpider(scrapy.Spider):
    name = "product_scrapper"
    allowed_domains = ["yarcheplus.ru"]
    start_urls = ["https://yarcheplus.ru/"]
    
    custom_settings = {
        "User-Agent": UserAgent().firefox
    }

    def parse(self, response, **kwargs):
        token = response.css('script::text').re_first(r'token\s*:\s*"([a-f0-9\-]+)"')

        categories = response.css('a.aJjLH4KAr::attr(href)').getall()

        for category_url in categories:
            yield response.follow(
                category_url,
                callback=self.parse_category,
                cb_kwargs={"category_url": category_url},
                meta={"token": token}
            )

    def parse_category(self, response, category_url):
        product_urls = response.css('.aUuHgqUxc a::attr(href)').getall()

        for product_url in product_urls:
            product_id = extract_id(product_url)

            yield response.follow(
                product_url,
                callback=self.parse_item,
                cb_kwargs={
                    "product_id": product_id,
                    "product_url": product_url,
                    "category_url": category_url
                },
                meta={**response.meta}
            )

        pagination_container = response.xpath('//div[contains(@class, "aft")]')

        if pagination_container:
            pages = pagination_container.xpath('.//a/@href').getall()

            for page in pages:
                yield response.follow(
                    page,
                    callback=self.parse_category,
                    cb_kwargs={"category_url": category_url},
                    meta={**response.meta}
                )

    def parse_item(self, response, product_id, product_url, category_url):
        query = {
            "query": q.product,
            "variables": i.product.format(product_id=product_id)
        }

        yield scrapy.Request(
            url="https://api.yarcheplus.ru/api/graphql",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "token": response.meta["token"],
                "Origin": "https://yarcheplus.ru",
                "Referer": "https://yarcheplus.ru"
            },
            body=json.dumps(query),
            callback=self.save_product_data
        )

    # TODO дописать подключение пайплайна и json
    def save_product_data(self):
        pass


def extract_id(url):
    match = re.search(r'-([0-9]+)(?:\?|$)', url)
    return match.group(1) if match else None
