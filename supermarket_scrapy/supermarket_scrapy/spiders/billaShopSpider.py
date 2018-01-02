# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 12:50:17 2017

@author: Philip Röggla

Needs: Downloader Middleware: 'supermarket_scrapy.middlewares.BillaShopFilter'
Needs: Downloader Middleware: 'supermarket_scrapy.middlewares.useChrome'
Needs: selenium Chrome

chrome warning: A parser blocking cross site script [...] is invoked via document.write.
The network request MAY be blocked in the browser in this or a future load due to poor
network connectivity. [...]

super slow!!!!!
"""
import re
from scrapy.spiders import SitemapSpider
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider

class BillaShopSpider(abstractShopSpider.AbstractShopSpider, SitemapSpider):
    name = 'BillaShop'
    sitemap_urls = ['https://shop.billa.at/sitemap']
    store = ['Billa']

    zutatenRegEx = re.compile('Zutaten.*?:')
    producerRegEx = re.compile('Name:\s+?(\w.*?)<', flags=re.DOTALL)
    sizeRegEx = re.compile('Nettogehalt:\s+?(\d+\.{0,1}\d*)\s+?([a-zA-Z]+)')

    def __init__(self, *args, **kwargs):
        super(BillaShopSpider, self).__init__(*args, **kwargs)
        self._setOUTPUT_()

    def parse(self, response):
        for product in self.parseProduct(response):
            yield product

    def getData(self, response=None, data=None):
        data = response.xpath('//div[@itemtype="http://schema.org/Product"]')
        return data

    def getName(self, response=None, data=None):
        name = data.xpath('./meta[@itemprop="name"]/@content')
        name = name.extract_first()
        return name

    def getIngredients(self, response=None, data=None):
        ingredients = data.xpath('.//h2[.="Zutaten"]/following-sibling::div/text()')
        ingredients = ingredients.extract_first()
        if not ingredients:
            return None
        ingredients = re.sub(self.zutatenRegEx, '', ingredients)
        ingredients = self.zutatenRegEx.sub('', ingredients)
        ingredients = self.usualIngridientsSplitting(ingredients)
        return ingredients

    def getGtin(self, response=None, data=None):
        'I believe the article id (at the end of the url) is the gtin-8'
        splitURL = response.url.split('/')
        gtin = splitURL[-1]
        gtin = gtin.replace('-','')
        return gtin

    def getBrand(self, response=None, data=None):
        brand = data.xpath('./meta[@itemprop="brand"]/@content')
        brand = brand.extract_first()
        return brand

    def getProducer(self, response=None, data=None):
        contact = data.xpath('.//div[@ng-repeat="contact in productDetail.lmiv.contacts"]')
        producer = contact.re_first(self.producerRegEx)
        return producer

    def getCategory(self, response=None, data=None):
        catLink = response.xpath(
                '//li[@itemprop="itemListElement"]/a[@dd-cookie="articlegroup"]/@href'
                                    )
        catLink = catLink.extract_first()
        if catLink:
            catLink = catLink.split('/')
            if len(catLink) >= 3:
                catLink = catLink[2]
                return catLink
            else:
                return None
        else:
            return None

    def getSize(self, response=None, data=None):
        returnDict = dict()
        size = data.re(self.sizeRegEx)
        if len(size) != 2:
            return None
        for item in size:
            if type(item) != str:
                return None
        amount, unit = size
        unit = unit.lower() # Gram -> gram
        if unit in self.units:  # gram -> g
            unit = self.units[unit]
        elif unit not in self.units.values():
            return None  # unknown
        returnDict['amount'] = amount
        returnDict['unit'] = unit
        return returnDict

    def getPrice(self, response=None, data=None):
        returnDict = dict()
        amount = data.xpath('.//meta[@itemprop="price"]/@content')
        amount = amount.extract_first()
        if amount:
            returnDict['amount'] = amount
        currency = data.xpath('.//meta[@itemprop="priceCurrency"]/@content')
        currency = currency.extract_first()
        if currency:
            returnDict['currency'] = currency
        return returnDict

    def getImageURL(self, response=None, data=None):
        imgURL = data.xpath('//*[@itemprop="image"]/@src')
        imgURL = imgURL.extract_first()
        return imgURL