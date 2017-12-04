# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 18:52:01 2017

@author: Philip Röggla

Needs: Downloader Middleware: 'supermarket_scrapy.middlewares.EdekaFilter'
"""
import re
from scrapy.spiders import SitemapSpider
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider
class EdekaShopSpider(abstractShopSpider.AbstractShopSpider, SitemapSpider):
    name = 'EdekaShop'
    sitemap_urls = ['https://www.edeka24.de/sitemaps/sitemap_0-products-0.xml']
    store = 'Edeka'
    
    xlmnsXPath = '//div[@xmlns]'
    brandRegEx = re.compile('zx_brand\s*=\s*\"(.+)\"')
    sizeAmountRegEx = re.compile('Inhalt\:\s+(\d+)\s*\w+')
    sizeUnitRegEx = re.compile('Inhalt\:\s+\d+\s*(\w+)')
    
    def __init__(self, *args, **kwargs):
        super(EdekaShopSpider, self).__init__(*args, **kwargs)
        self._setOUTPUT_()
        
    def parse(self, response):
        for product in self.parseProduct(response):
            yield product
        
    def getData(self, response=None, data=None):
        xlmns = response.xpath(self.xlmnsXPath)
        return xlmns
    
    def getName(self, response=None, data=None):
        name = data.xpath('.//div[@property="gr:name"]/@content')
        name = name.extract_first()
        return name
    
    def getIngredients(self, response=None, data=None):
        ingredients = response.xpath('//span[@class="listValue"]/text()')
        ingredients = ingredients.extract_first()
        if ingredients:
            ingredients = ingredients.replace(" *aus biologischer Landwirtschaft", '')
            ingredients = ingredients.replace('°', '')
            ingredients = self.usualIngridientsSplitting(ingredients)
            return ingredients
        else:
            return None
    
    def getGtin(self, response=None, data=None):
        gtin = data.xpath('.//div[@property="gr:hasEAN_UCC-13"]/@content')
        gtin = gtin.extract_first()
        return gtin
    
    def getBrand(self, response=None, data=None):
        brand = response.xpath('//script')
        brand = brand.re_first(self.brandRegEx)
        return brand
    
    def getProducer(self, response=None, data=None):
        producer = response.xpath(
'//span[.="Verantwortliches Lebensmittelunternehmen:"]/following::span[1]/text()'
                                    )
        producer = producer.extract_first()
        return producer
    
    def getCategory(self, response=None, data=None):
        splitUrl = response.url.split('/')
        if len(splitUrl) >= 5:
            return splitUrl[4]
        else:
            return None
    
    def getSize(self, response=None, data=None):
        returnDict = dict()
        size = response.css('div .product-details')
        if size:
            amount = size.re_first(self.sizeAmountRegEx)
            unit = size.re_first(self.sizeUnitRegEx)
            if amount:
                returnDict['amount'] = amount
            if unit:
                returnDict['unit'] = unit
        return returnDict
    
    def getPrice(self, response=None, data=None):
        returnDict = dict()
        currency = data.xpath('.//div[@property="gr:hasCurrency"]/@content')
        currency = currency.extract_first()
        if currency:
            returnDict['currency'] = currency
        amount = data.xpath('.//div[@property="gr:hasCurrencyValue"]/@content')
        amount = amount.extract_first()
        if amount:
            returnDict['amount'] = amount
        return returnDict
    
    def getImageURL(self, response=None, data=None):
        img = data.xpath('.//div[@rel="foaf:depiction v:image"]/@resource')
        img = img.extract_first()
        return img