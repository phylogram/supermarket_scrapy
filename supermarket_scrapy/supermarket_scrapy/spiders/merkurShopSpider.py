# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 18:02:21 2017

@author: Philip Röggla

Needs: Downloader Middleware: 'supermarket_scrapy.middlewares.useChrome'
Needs: Selenium Chrome
"""
import re
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider
from scrapy.spiders import SitemapSpider

class MerkurShopSpider(abstractShopSpider.AbstractShopSpider, SitemapSpider):
    name = 'MerkurShop'
    sitemap_urls = ['https://www.merkurmarkt.at/sitemap_products.xml']
    allowed_domains = ['merkurmarkt.at']
    store = ['Merkur']
    
    brandRegEx = re.compile(r"\\x22brand\\x22:\\x22(.+?)\\x22")
    
    def __init__(self, *args, **kwargs):
        super(MerkurShopSpider, self).__init__(*args, **kwargs)
        self._setOUTPUT_()
        
    def parse(self, response):
        for product in self.parseProduct(response):
            yield product
        
    def getName(self, response=None, data=None):
        name = response.xpath('//h1[@itemprop="name"]')
        name = name.extract_first()
        return name
    
    def getIngredients(self, response=None, data=None):
        ingredientString = response.xpath('//tr[@ng-if="lmiv.data.ingredients"]/td/text()')
        ingredientString = ingredientString.extract_first()
        if ingredientString:
            ingredientString = ingredientString.replace('Zutaten: ', '')
            ingredientString = self.usualIngridientsSplitting(ingredientString)
        return ingredientString
    
    def getGtin(self, response=None, data=None):
        splitURL = response.url.split('/')
        if len(splitURL) >= 5:
            gtin = splitURL[4]
            gtin = gtin.replace('-', '')
            return gtin
        else:
            return None
    
    def getBrand(self, response=None, data=None):
        brand = response.selector.re_first(self.brandRegEx)
        return brand
    
    def getProducer(self, response=None, data=None):
        producer = response.xpath(
'//tr[@ng-repeat="contact in lmiv.data.contacts"]/td[.="Name"]/following-sibling::td/text()'
                                    )
        producer = producer.extract_first()
        return producer
    
    # no category ... To do
    
    def getSize(self, response=None, data=None):
        returnDict = dict()
        size = response.xpath(
'//tr[@ng-repeat="spec in lmiv.data.measurements"]/td[contains(., "gehalt:")]/following-sibling::*'
                                )
        amount = size.xpath('./span[@ng-bind="spec.value"]/text()')
        amount = amount.extract_first()
        if amount:
            returnDict['amount'] = amount
        unit = size.xpath('./span[@ng-bind-html="spec.unit | abbreviation"]/text()')
        unit = unit.extract_first()
        if unit:
            unit = unit.lower()
            if unit in self.units:
                unit = self.units[unit]
            returnDict['unit'] = unit
        return returnDict
    
    def getPrice(self, response=None, data=None):
        returnDict = dict()    
        price = price = response.css('.price--current')
        
        mainDigits = price.xpath('./text()')
        mainDigits = mainDigits.extract_first()
        afterDecimal = price.xpath('./span[contains(@class, "sup")]/text()')
        afterDecimal = afterDecimal.extract_first()
        
        if afterDecimal and mainDigits:
            amount = mainDigits + afterDecimal
        elif not afterDecimal and mainDigits:
            amount = mainDigits
            if [-1] == '.':
                amount = amount[:-1] # dec point with no .\d\d
        else:
            amount = None
        if amount:
            returnDict['amount'] = amount
        unit = price.xpath('./meta[@itemprop="priceCurrency"]/@content')
        unit = unit.extract_first()
        if unit:
            returnDict['currency'] = unit
        return returnDict
    
    def getImageURL(self, response=None, data=None):
        imageURL = response.xpath('/html/head/meta[@property="og:image"]/@content')
        imageURL = imageURL.extract_first()
        return imageURL