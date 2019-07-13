# -*- coding: utf-8 -*-
import scrapy

class StaplesSpider(scrapy.Spider):
    name = 'staplesspider'
    start_urls = ["http://www.staples.cn/"]

    def parse(self, response):
        for category in response.css('.cf_c a'):
            yield response.follow(category, self.parse_page,
                meta={'category': category.css('::text').get()})

    def parse_page(self, response):
        for item in response.css('.cg_pro'):
            yield {
                'category': response.meta['category'],
                'link': item.css('a.proImg').attrib['href'],
                'img': item.css('img').attrib['src'],
                'gift': item.css('.pro_gift::text').get(),
                'title': item.css('.pro_name').attrib['title'],
                'id': item.css('.pro_code::text').get(),
                'price': ''.join(item.css('.pro_price *::text').getall())
            }
        for next in response.css('.next'):
            if 'keyval' in next.attrib:
                yield response.follow(next.attrib['keyval'], self.parse_page,
                    meta={'category': response.meta['category']})
