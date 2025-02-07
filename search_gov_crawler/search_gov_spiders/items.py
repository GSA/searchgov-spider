""" Define here the models for your scraped items
See documentation in:
https://docs.scrapy.org/en/latest/topics/items.html """

import scrapy


class SearchGovSpidersItem(scrapy.Item):
    """Class for Item which is a container for every returned scraped page"""
    html_content = scrapy.Field()
    url = scrapy.Field()
    output_target = scrapy.Field()
