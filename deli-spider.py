# -*- coding: utf-8 -*-
import scrapy
import re
from collections import OrderedDict
from json import loads

class DeliSpider(scrapy.Spider):
    name = 'delispider'
    start_urls = ['http://b2b.nbdeli.com/index.aspx']

    def parse(self, response):
        for category in response.css('dd a'):
            yield response.follow(category, self.parse_page, meta={
                'category': category.attrib['title']
            })

    def parse_page(self, response):
        items = OrderedDict()
        for item in response.css('.recommen_goods_li'):
            id = re.match(r'^\s*商品编号：(\d+)\s*$',
                item.css('.recommen_goods_sku::text').get()).group(1)
            items[id] = {
                'category': response.meta['category'],
                'link': item.css('.recommen_goods_item a').attrib['href'],
                'image': item.css('.recommen_goods_item img').attrib['data-original'],
                'title': item.css('.recommen_goods_name a::text').get(),
                'subtitle': item.css('.recommen_goods_name font::text').get(),
                'id': id
            }
        for next_page in response.css('#MainPlace_pageChanger_Main_Bottom_'
                'HyperLinkBottomNextImage'):
            yield response.follow(next_page, self.parse_page, meta={
                'category': response.meta['category']
            })
        meta = {
            'data': items,
            'item quantity': re.search(r'var itemQty = new ItemQty\("([^"]+)",'
                r' "lbl_ItemQty_"\);', response.text).group(1),
            'item price': re.search(r'var itemPrice = new ItemAvergePrice\("([^"]+)",'
                r' "ItemPrice", "ItemAveragePrice"\);', response.text).group(1),
        }
        yield scrapy.FormRequest('http://b2b.nbdeli.com/Goods/Services/AsyncItem.ashx',
            formdata={
                'action': 'GetItemQty',
                'itemids': meta['item quantity'],
                'callback': 'foo'
            }, meta=meta, callback=self.parse_item_quantity)
        
    def parse_item_quantity(self, response):
        meta = response.meta
        data = loads(re.match(r'foo\(([^)]+)\)', response.text)
            .group(1))['Data']['data']
        for item in data:
            origin_item = meta['data'][item['ItemId']]
            origin_item['quantity'] = item['ItemQty']
            origin_item['status'] = item['Status']
        yield scrapy.FormRequest('http://b2b.nbdeli.com/Goods/Services/'
            'AsyncItemPrice.ashx', formdata={
                'action': 'GetItemPrice',
                'ItemIds': meta['item price'],
                'hasAveragePrice': '1',
                'callback': 'foo'
            }, meta={'data': meta['data']}, callback=self.parse_item_price)
    
    def parse_item_price(self, response):
        data = loads(re.match(r'foo\(([^)]+)\)', response.text)
            .group(1))['Data']['data']
        for item in data:
            origin_item = response.meta['data'][item['ItemId']]
            origin_item['price'] = item['Price']
            origin_item['average price'] = item['AveragePrice']
            origin_item['original price'] = item['OriginalPrice']
            origin_item['price unit'] = item['UnitName']
        yield from response.meta['data'].values()
