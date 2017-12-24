# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 13:23:37 2017

@author: Philip Röggla
"""
import re
import scrapy
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider

class KauflandShopSpider(abstractShopSpider.AbstractShopSpider, scrapy.Spider):
    name = 'KauflandShop'
    start_urls = ['https://shop.kaufland.de/search?sort=relevance&pageSize=48&source=search']
    allowed_domains = ['shop.kaufland.de'] # actually not really needed
    store = 'Kaufland'
    sizeRegEx = re.compile('([\d]+?)([a-zA-Z]+)[\W]*')
    priceAmountRegEx = re.compile('([\d]+?\.{0,1}[\d]*?)\s+?[\W]')
    
    def __init__(self, *args, **kwargs):
        super(KauflandShopSpider, self).__init__(*args, **kwargs)
        self._setOUTPUT_()
    
    def parse(self, response):
        # parse products:
        products = response.css(".product-tile-container")
        products = products.xpath('./article/a/@href')
        for product in products:
            yield response.follow(product, self.parseProduct)
        
        # get next Page
        nextPage = response.xpath('//a[@title="Weiter"]/@href').extract_first()
        if nextPage:
            yield response.follow(nextPage)
    
    def getName(self, response=None, data=None):
        name = response.css('h1.product-info--title')
        name = name.extract_first()
        return name

    def getIngredients(self, response=None, data=None):
        ingredientString = response.xpath('.//h4[.="Zutatenliste"]/following-sibling::p/text()')
        ingredientString = ingredientString.extract_first()
        ingredientString = self.usualIngridientsSplitting(ingredientString)
        return ingredientString

    def getProducer(self, response=None, data=None):
        producer = response.xpath('.//h4[.="Name Hersteller"]/following-sibling::p/text()')
        producer = producer.extract_first()
        return producer

    def getCategory(self, response=None, data=None):
        category = response.css('ol.breadcrumb__list')
        category = category.xpath('./li[2]/a/span/@title') # hope this does not brake
        category = category.extract_first()
        return category

    def getSize(self, response=None, data=None):
        returnDict = dict()
        size = response.css('h1.product-info--title')
        size = size.re(self.sizeRegEx)
        if len(size) == 2:
            amount, unit = size
            returnDict['amount'] = amount
            returnDict['unit'] = unit
        return returnDict

    def getPrice(self, response=None, data=None):
        returnDict = dict()
        price = response.xpath('//div[contains(@class,"product-info--regularprice")]/text()')
        amount = price.re_first(self.priceAmountRegEx)
        unit = 'EUR' # everytime
        if amount:
            returnDict['amount'] = amount
            returnDict['currency'] = unit
        return returnDict

    def getImageURL(self, response=None, data=None):
        image = response.xpath(
'//div[contains(@class, "product-media__image")]/picture/img/@data-img-src'
                                ).extract_first()
        return image
        