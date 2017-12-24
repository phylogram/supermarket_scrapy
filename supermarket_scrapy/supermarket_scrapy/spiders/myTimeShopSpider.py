# -*- coding: utf-8 -*-
'''
Created on Sat Dec  2 18:02:21 2017

@author: Philip Röggla

Needs: Downloader Middleware: 'supermarket_scrapy.middlewares.MyTimeShopFilter'

Schema: http://graph.facebook.com/schema/og/product
'''
import re
from scrapy.spiders import SitemapSpider
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider

class MyTimeShopSpider(abstractShopSpider.AbstractShopSpider, SitemapSpider):
    name = 'MyTimeShop'
    sitemap_urls = ['https://www.mytime.de/sitemap.xml']
    store = ['myTime.de'] #Check

    sizeRegEx = re.compile('.+?\(([\d]+?)[\s]*?([a-z]+?)\)')
 
    def __init__(self, *args, **kwargs):
        super(MyTimeShopSpider, self).__init__(*args, **kwargs)
        self._setOUTPUT_()
        
    def parse(self, response):
        for product in self.parseProduct(response):
            yield product
            
    def getData(self, response=None, data=None):
        head = response.xpath('/html/head')
        return head
    
    def getName(self, response=None, data=None):
        name = data.xpath('./meta[@property="og:title"]/@content')
        name = name.extract_first()
        return name
    
    def getIngredients(self, response=None, data=None):
        ingredients = response.xpath('.//div[.="Zutaten"]/following-sibling::div/text()')
        ingredients = ingredients.extract_first()
        ingredients = self.usualIngridientsSplitting(ingredients)
        return ingredients
    
    def getGtin(self, response=None, data=None):
        gtin =  response.xpath('//input[@name="data-ean"]/@value')
        gtin = gtin.extract_first()
        return gtin
    
    def getBrand(self, response=None, data=None):
        brand = data.xpath('./meta[@itemprop="brand"]/@content')
        brand = brand.extract_first()
        return brand
    
    def getProducer(self, response=None, data=None):
        producer = response.xpath('//div[.="Inverkehrbringer"]/following-sibling::div')
        producer = producer.extract_first()
        return producer
    
    def getCategory(self, response=None, data=None):
        category = response.xpath('./meta[@itemprop="category"]/@content')
        category = category.extract_first()
        return category
    
    def getSize(self, response=None, data=None):
        returnDict =dict()
        size = response.xpath('//h1[@id="product-name"]')
        size = size.re(self.sizeRegEx)
        if len(size) == 2:
            amount, unit = size
            returnDict['amount'] = amount
            returnDict['unit'] = unit
        return returnDict
    
    def getPrice(self, response=None, data=None):
        returnDict = dict()    
        amount = response.xpath('./meta[@property="product:price:amount"]/@content')
        amount = amount.extract_first()
        if amount:
            returnDict['amount'] = amount
        currency = currency = response.xpath('./meta[@property="product:price:currency"]/@content')
        currency = currency.extract_first()
        if currency:
            returnDict['currency'] = currency
        return returnDict
    
    def getImageURL(self, response=None, data=None):
        img = response.xpath('./meta[@property="og:image"]/@content')
        img = img.extract_first()
        return img
        