# -*- coding: utf-8 -*-
import scrapy
from time import time
from urllib.parse import urlencode
from json import loads, dumps

class CnncmallSpider(scrapy.Spider):
    name = 'cnncmallspider'

    def start_requests(self):
        yield scrapy.Request('https://www.cnncmall.com/scm-cnnc-oauth-web/obs/business'
            '/product/Catrgory/query?' + urlencode({"t": int(time())}))

    def parse(self, response):
        result = loads(response.text)['data']
        def travel(list):
            for item in list:
                yield scrapy.Request('https://www.cnncmall.com/scm-cnnc-oauth-web/obs/'
                    'business/product/ProductSearch/search?' +
                    urlencode({"t": int(time())}), callback=self.parse_first_page, 
                    method='POST', body=dumps({
                        "brandName": None,
                        "categoryCode": None,
                        "categoryName": None,
                        "channelName": None,
                        "isCategoryQuery": None,
                        "limit": 12,
                        "sort": None,
                        "webCategoryCode": item['nodeCode'],
                        "webCategoryName": item['nodeName']
                    }), headers={'Content-Type':'application/json'}, meta={
                        "category code": item['nodeCode'],
                        "category name": item['nodeName']
                    })
                yield from travel(item['childNodeList'])
        yield from travel(result)
    
    def parse_first_page(self, response):
        for page in range(loads(response.text)['data']['result']['totalPage']):
            yield scrapy.Request('https://www.cnncmall.com/scm-cnnc-oauth-web/obs/'
                'business/product/ProductSearch/search?' +
                urlencode({"t": int(time())}), callback=self.parse_page, 
                method='POST', body=dumps({
                    "categoryCode": "",
                    "categoryName": "",
                    "currentPage": page + 1,
                    "isCategoryQuery": False,
                    "limit": 12,
                    "sort": None,
                    "start": 12 * page,
                    "webCategoryCode": response.meta['category code'],
                    "webCategoryName": response.meta['category name']
                }), headers={'Content-Type':'application/json'}, meta={
                    "category code": response.meta['category code'],
                    "category name": response.meta['category name'],
                    "page": page
                })

    def parse_page(self, response):
        for item in loads(response.text)['data']['result']['root']:
            yield {
                'web category code': response.meta['category code'],
                'web category name': response.meta['category name'],
                'page': response.meta['page'] + 1,
                'key': item['key'],
                'product id': item['productId'],
                'product title': item['productTitle'],
                'product name': item['productName'],
                'image url': item['imageUrl'],
                'price str': item['priceStr'],
                'is post': item['isPost'],
                'sold num': item['soldNum'],
                'brand code': item['brandCode'],
                'brand name': item['brandName'],
                'category code': item['categoryCode'],
                'category name': item['categoryName'],
                'supplier name': item['supplierName'],
                'spec sign': item['specSign']
            }
