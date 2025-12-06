import scrapy

class ProductItem(scrapy.Item):
    product_url = scrapy.Field()
    category = scrapy.Field()
    sku = scrapy.Field()
    name = scrapy.Field()
    images = scrapy.Field()
    price_regular = scrapy.Field()
    price_discount = scrapy.Field()
    description = scrapy.Field()
    attributes = scrapy.Field()
    ingredients = scrapy.Field()
    rating = scrapy.Field()
    reviews_count = scrapy.Field()
    reviews = scrapy.Field()
    date_scraped = scrapy.Field()