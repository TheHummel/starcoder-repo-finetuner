# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class StockItem(scrapy.Item):
    isin = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    change_absolute = scrapy.Field()
    change_percent = scrapy.Field()
