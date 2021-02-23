# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AdmitadItem(scrapy.Item):
    name = scrapy.Field()
    img = scrapy.Field()
    price = scrapy.Field()
    old_price = scrapy.Field()
    sale_price = scrapy.Field()
    sku = scrapy.Field()
    description = scrapy.Field()
    parameters = scrapy.Field()
    category = scrapy.Field()
    brand = scrapy.Field()
    color = scrapy.Field()
    size = scrapy.Field()
    country = scrapy.Field()
    site_name = scrapy.Field()
    ref = scrapy.Field()
    product_type = scrapy.Field()
    currency = scrapy.Field()
