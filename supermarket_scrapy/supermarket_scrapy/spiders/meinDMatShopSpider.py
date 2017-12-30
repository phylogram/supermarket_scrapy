# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 15:30:09 2017

@author: Philip Röggla

Needs: Downloader Middleware: 'supermarket_scrapy.middlewares.skipNonProductsMeinDM'
"""
import re
from scrapy.spiders import SitemapSpider
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider

class MeinDMatShopSpider(abstractShopSpider.AbstractShopSpider, SitemapSpider):
    name = 'MeinDMatShop'
    sitemap_urls = ['https://www.meindm.at/nl/sitemap/sitemap-shop.xml']
    allowed_domains = ['meindm.at']
    store = ['meinDM.at']
    
    sizeRegEx = re.compile('(\d+?[\.,]{0,1}\d{0,3})\s([gml]{1,2})') # only gets g and ml

    def __init__(self, *args, **kwargs):
        super(MeinDMatShopSpider, self).__init__(*args, **kwargs)
        self._setOUTPUT_()

    def parse(self, response):
        for product in self.parseProduct(response):
            yield product
        
    # Single data retrievers
    def getName(self, response=None, data=None):
        name = response.xpath('//h1[@itemprop="name"]/text()')
        name = name.extract_first()
        return name

    def getIngredients(self, response=None, data=None):
        'nothing special to replace here'
        ingredientSelector = response.css('.tab-ingredients')
        ingredientSelector = ingredientSelector.xpath('.//p')
        ingredientString = ingredientSelector.extract_first()
        ingredientString = self.usualIngridientsSplitting(ingredientString)
        return ingredientString

    def getGtin(self, response=None, data=None):
        gtin = response.xpath('//meta[@itemprop="gtin13"]/@content')
        gtin = gtin.extract_first()
        return gtin

    def getBrand(self, response=None, data=None):
        brand = response.xpath('//meta[@itemprop="brand"]/@content')
        brand = brand.extract_first()
        return brand

    def getCategory(self, response=None, data=None):
        splitURL = response.url.split('/')
        if len(splitURL) >= 7:
            category = splitURL[6]
            return category
        else:
            return None

    def getSize(self, response=None, data=None):
        'size is in a text field and mixes with other number - unit data.'
        size = response.css('.price_details')
        size = size.re(self.sizeRegEx)
        if len(size) == 2:
            amount, unit = size
            return {'amount': amount, 'unit': unit}
        else:
            return None

    def getPrice(self, response=None, data=None):
        returnDict = dict()
        price = response.xpath('//*[@itemprop="offers"]')
        amount = price.xpath('./meta[@itemprop="price"]/@content')
        amount = amount.extract_first()
        unit = price.xpath('./meta[@itemprop="priceCurrency"]/@content')
        unit = unit.extract_first()
        if amount:
            returnDict['amount'] = amount
        if unit:
            returnDict['currency'] = unit
        return returnDict

    def getImageURL(self, response=None, data=None):
        imageURL = response.xpath('//meta[@property="og:image"]/@content')
        imageURL = imageURL.extract_first()
        return imageURL