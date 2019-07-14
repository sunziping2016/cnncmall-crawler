# -*- coding: utf-8 -*-
import scrapy
import re
import time
from urllib.parse import urlencode, urljoin
from json import loads
from collections import OrderedDict

class JdDeliSpider(scrapy.Spider):
    name = 'jddelispider'
    start_urls = ['https://mall.jd.com/index-1000001132.html']

    def parse(self, response):
        for category in response.css('.nice_content .link_box'):
            link = urljoin(response.url, category.attrib['href'])
            category_id = re.match(r'^https://deli\.jd\.com/view_search-'
                r'\d+-(\d+)-\d+-\d+-\d+-\d+\.html$', link).group(1)
            yield scrapy.Request('https://module-jshop.jd.com/module/'
                'getModuleHtml.html?' +  urlencode({
                    'orderBy': '5',
                    'direction': '1',
                    'pageNo': '1',
                    'categoryId': category_id,
                    'pageSize': '24',
                    'pagePrototypeId': '8',
                    'pageInstanceId': '18760345',
                    'moduleInstanceId': '170723611',
                    'prototypeId': '34',
                    'templateId': '977439',
                    'appId': '395795',
                    'layoutInstanceId': '170723611',
                    'origin': '0',
                    'shopId': '1000001132',
                    'venderId': '1000001132',
                    'callback': 'jshop_module_render_callback',
                    '_': int(time.time() * 1000)
                }), headers={
                    'Referer': link
                }, callback=self.parse_page, meta={
                    'category': category.css('::text').get(),
                    'category id': category_id,
                    'page no': 1
                })
    
    def parse_page(self, response):
        body = loads(re.match(r"^jshop_module_render_callback\((.*)\)$",
            response.text).group(1))['moduleText']
        selector = scrapy.Selector(text=body)
        items = OrderedDict()
        for item in selector.css('.user_fyxs .jItem'):
            price_id = item.css('.jdNum').attrib['jdprice']
            items[price_id] = {
                'category': response.meta['category'],
                'link': item.css('.jPic a').attrib['href'],
                'image': item.css('img').attrib['src'],
                'title': item.css('.jDesc').attrib['title'],
                'price prefix': item.css('.jRmb::text').get()
            }
        for next_page in selector.css('.jPage a'):
            if next_page.css('::text').get() != '下一页':
                continue
            link = urljoin(response.url, next_page.attrib['href'])
            yield scrapy.Request('https://module-jshop.jd.com/module/'
                'getModuleHtml.html?' +  urlencode({
                    'orderBy': '5',
                    'direction': '1',
                    'pageNo': response.meta['page no'] + 1,
                    'categoryId': response.meta['category id'],
                    'pageSize': '24',
                    'pagePrototypeId': '8',
                    'pageInstanceId': '18760345',
                    'moduleInstanceId': '170723611',
                    'prototypeId': '34',
                    'templateId': '977439',
                    'appId': '395795',
                    'layoutInstanceId': '170723611',
                    'origin': '0',
                    'shopId': '1000001132',
                    'venderId': '1000001132',
                    'callback': 'jshop_module_render_callback',
                    '_': int(time.time() * 1000)
                }), headers={
                    'Referer': link
                }, callback=self.parse_page, meta={
                    'category': response.meta['category'],
                    'category id': response.meta['category id'],
                    'page no': response.meta['page no'] + 1
                })
        if len(items):
            yield scrapy.Request('https://p.3.cn/prices/mgets?' +
                urlencode({
                    'callback': 'foo',
                    'source': 'jshop',
                    'area': '1_2800_0_0',
                    'skuids': ''.join(['J_%s,' % id for id in items.keys()]),
                    '_': int(time.time() * 1000)
                }), callback=self.parse_price, meta={
                    'data': items
                })
    
    def parse_price(self, response):
        body = loads(re.match(r"^foo\((.*)\);$", response.text).group(1))
        data = response.meta['data']
        for item in body:
            id = re.match(r'^J_(\d+)$', item['id']).group(1)
            data[id]['price'] = item['p']
        yield from data.values()
