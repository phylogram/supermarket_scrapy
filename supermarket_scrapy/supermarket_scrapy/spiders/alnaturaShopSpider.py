# -*- coding: utf-8 -*-
"""
Created on Sat Nov 25 17:48:39 2017

@author: Philip Röggla
http://schema.org/Product is used here
"""
import re
from scrapy.spiders import SitemapSpider
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider

class AlnaturaShopSpider(abstractShopSpider.AbstractShopSpider, SitemapSpider):
    name = 'AlnaturaShop'
    sitemap_urls = ['https://www.alnatura-shop.de/medias/PRODUCT-de-EUR-479627737118262662.xml?context=bWFzdGVyfHJvb3R8NzI2MDI1fHRleHQveG1sfGhkOS9oZTcvOTA5NjQ3ODU4ODk1OC54bWx8N2JmNzFlOWQxM2Q3YTAwMWQ5MzFiOTk1NGQ0OTdjMGVhYWE0YTBiY2U5YmYyNDJkNzkyNTZmODhkNTlmNWMwNQ']
    store = 'Alnatura'
    
    ingredientsRegEx = re.compile(' \* aus biologischer[\s]+?Landwirtschaft')
    
    def __init__(self, *args, **kwargs):
        super(AlnaturaShopSpider, self).__init__(*args, **kwargs)
        self._setOUTPUT_()    
    
    def parse(self, response):
        for product in self.parseProduct():
            yield product
    
    def getName(self, response=None, data=None):
        name = response.xpath(
                '//*[@itemtype="https://schema.org/Product"]//*[@itemprop="name"]//h1/text()'
                                )
        name = name.extract_first()
        return name
    
    def getIngredients(self, response=None, data=None):
       ingredients = response.xpath('.//td[.="Zutaten"]/following-sibling::*/text()')
       ingredients = ingredients.extract_first()
       if ingredients:
           ingredients = re.sub(self.ingredientsRegEx, '', ingredients)
           ingredients = self.usualIngridientsSplitting(ingredients)
       return ingredients
   
    def getGtin(self, response=None, data=None):
        gtin =  response.xpath('//*[@itemprop="gtin14"]/@content')
        gtin = gtin.extract_first()
        return gtin
    
    def getBrand(self, response=None, data=None):
        brand = response.xpath('//*[@itemprop="brand"]/*[@itemprop="name"]/@content')
        brand = brand.extract_first()
        return brand
    
    def getProducer(self, response=None, data=None):
        producer = response.xpath(
                '//td[.="verantw. Lebensmittelunternehmer"]/following::td[1]/text()'
                                    )
        producer = producer.extract_first()
        return producer
    
    def getCategory(self, response=None, data=None):
        splitURL = response.url.split('/')
        if len(splitURL) >= 4:
            category = splitURL[3]
            return category
        else:
            return None
    
    def getSize(self, response=None, data=None):
        returnDict = dict()
        size = response.xpath('//*[@itemprop="weight"]')
        amount = size.xpath('./*[@itemprop="value"]/@content')
        amount = amount.extract_first()
        if amount:
            returnDict['amount'] = amount
        unit = size.xpath('./*[starts-with(@itemprop, "unit")]/@content')
        unit = unit.extract_first()
        if unit:
            returnDict['unit'] = unit
        return returnDict
    
    def getPrice(self, response=None, data=None):
        returnDict = dict()
        price = response.xpath('//*[@itemprop="offers"]')
        if price:
            amount = price.xpath('./*[@itemprop="price"]/@content')
            amount = amount.extract_first()
            if amount:
                returnDict['amount'] = amount
            currency = price.xpath('./*[@itemprop="priceCurrency"]/@content')
            currency = currency.extract_first()
            if currency:
                returnDict['currency'] = currency
        return returnDict
    
    def getImageURL(self, response=None, data=None):
        img = response.xpath('//*[@itemprop="image"]/@src')
        img = img.extract_first()
        return img