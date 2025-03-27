# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsSpiderItem(scrapy.Item):
    headline = scrapy.Field()
    topic = scrapy.Field()
    url = scrapy.Field()
    site = scrapy.Field()
