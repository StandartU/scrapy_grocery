import scrapy

class ProductSpider(scrapy.Spider):
    name = "product_scrapper"
    allowed_domains = ["yarcheplus.ru"]
    start_urls = ["https://yarcheplus.ru/"]

    # TODO парсинг всех категорий
    def parse(self, response, **kwargs):
        pass

    # TODO парсинг всех продуктов в категории и их айди
    def parse_category(self, response):
        pass

    # TODO ql запрос для получения всех данных по продукту
    def parse_item(self, response):
        pass