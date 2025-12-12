import scrapy
import re
import json
from fake_useragent import UserAgent

class ProductSpider(scrapy.Spider):
    name = "product_scrapper"
    allowed_domains = ["yarcheplus.ru"]
    start_urls = ["https://yarcheplus.ru/"]
    
    custom_settings = {
        "User-Agent": UserAgent().firefox
    }

    def parse(self, response, **kwargs):
        token = response.css('script::text').re_first(r'token\s*:\s*"([a-f0-9\-]+)"')
        self.token = token

        categories = response.css('a.aJjLH4KAr::attr(href)').getall()

        for url in categories:
            yield response.follow(url, callback=self.parse_category)

    def parse_category(self, response):
        product_links = response.css('.aUuHgqUxc a::attr(href)').getall()

        for url in product_links:
            product_id = extract_id(url)

            yield response.follow(
                url,
                callback=None,
                cb_kwargs={"product_id": product_id}
            )

        pagination_container = response.xpath('//div[contains(@class, "aft")]')

        if pagination_container:
            pages = pagination_container.xpath('.//a/@href').getall()

            for page in pages:
                yield response.follow(page, callback=self.parse_category)

    # TODO ql запрос для получения всех данных по продукту
    def parse_item(self, response, product_id):
        query = {
            "query": "...GraphQL-запрос...",
            "variables": {"id": product_id, "similarProductsInput": {"filter": {"similarByProductId": product_id},
                                                                     "page": {"page": 1, "limit": 6}}}
        }

        yield scrapy.Request(
            url="https://api.yarcheplus.ru/api/graphql",
            method="POST",
            headers={
                "Content-Type": "application/json",
                "token": self.token,
                "Origin": "https://yarcheplus.ru",
                "Referer": "https://yarcheplus.ru",
                "User-Agent": "Mozilla/5.0 ..."
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
