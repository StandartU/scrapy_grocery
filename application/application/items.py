# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    product_url = scrapy.Field()
    category_url = scrapy.Field()
    article = scrapy.Field()
    name = scrapy.Field()
    images_url = scrapy.Field()
    price_regular = scrapy.Field()
    price_discount = scrapy.Field()
    description = scrapy.Field()
    characteristics = scrapy.Field()
    compound = scrapy.Field()
    rating = scrapy.Field()
    reviews_count = scrapy.Field()
    reviews = scrapy.Field()
    date_scraped = scrapy.Field()