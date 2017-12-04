# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 10:17:18 2017

@author: Philip Röggla


Workflow parse():

for every category: parseCategories:
    for every product in response parse products() and get num of hits:
        for every product parse product(p1)
    for every page(p2 - num of hits) parse productPage():
        for every product in response parse products():
            for every product parse product()
for every product in response DMBrands parse roducts and get num of hits:
    for every product parse product(p1)
for every page(p2 - num of hits) parse productPage():
    for every product in response parse products():
        for every product parse product()
"""

import json
import re
import scrapy
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider

class DMShopSpider(abstractShopSpider.AbstractShopSpider, scrapy.Spider):
    name = 'DMShop'
    store = 'dm'
    
    start_urls = ['https://www.dm.de/']
    allowed_domains = ['dm.de'] # just to be safe
    
    base_api_url = 'https://services.dm.de/websearch/search/pues?type=product&tenant=de_mcr&q=&categoryId={categoryID}&pageSize=48&sort=relevance&cp={pageID}&productQuery=&initialProductQuery=&hiddenFacets='
    dmProdukteAPI = 'https://services.dm.de/websearch/search/pues?type=product&tenant=de_mcr&targetSystem=live&q=&categoryId=&pageSize=48&sort=relevance&cp={pageID}&productQuery=%3Arelevance%3Abrand%3Ababylove|true%3Abrand%3ABalea|true%3Abrand%3ABalea%20MEN|true%3Abrand%3ADAS%20gesunde%20PLUS|true%3Abrand%3ADein%20Bestes|true%3Abrand%3ADenkmit|true%3Abrand%3ADONTODENT|true%3Abrand%3Aebelin|true%3Abrand%3AJessa|true%3Abrand%3Ap2%20cosmetics|true%3Abrand%3AParadies|true%3Abrand%3APrinzessin%20Sternenzauber|true%3Abrand%3AProfissimo|true%3Abrand%3ASauB%C3%A4r|true%3Abrand%3AS-quitofree|true%3Abrand%3ASUNDANCE|true%3Abrand%3AVISIOMAX|true%3Abrand%3Aalverde%20NATURKOSMETIK|true%3Abrand%3ASanft%26Sicher|true%3Abrand%3ASaugstark%26Sicher|true%3Abrand%3ASoft%26Sicher|true%3Abrand%3Adm%20Bio|true&hiddenFacets=brand'
    

    categories = {
                    'Tierprodukte': '070000',
                    'Make-Up': '010000',
                    'Pflege & Duft': '020000',
                    'Haar': '110000',
                    'Gesundheits-Produkte': '030000',
                    'Ernährungs-Produkte': '040000',
                    'Baby &kind': '050000',
                    'Haushalt': '060000'
            }
    

    zutatenSubRegEx = re.compile('<dd>.*Zutaten:\s*', flags=re.DOTALL)
    
    def __init__(self, *args, **kwargs):
        super(DMShopSpider, self).__init__(*args, **kwargs)
        self._setOUTPUT_()

    def parse(self, response):
        for category in self.categories.values():
            url = self.base_api_url.format(categoryID=category, pageID=1)
            request = scrapy.Request(url, callback=self.parseCategories)
            request.meta['category'] = category
            yield request
        url = self.dmProdukteAPI.format(pageID=1)
        yield response.follow(url, self.parseDMBrands)
    
    def parseDMBrands(self, response):
        j = json.loads(response.text)
        for product in self.parseProducts(j):
            yield product
        hits = j['resultParams']['numHits']
        maxPage = hits//48 + 1
        for page in range(2, maxPage + 1):
            url = self.dmProdukteAPI.format(pageID=page)
            yield response.follow(url, callback=self.parseProductPage)
            
    def parseCategories(self, response):
        j = json.loads(response.text)
        for product in self.parseProducts(j):
            yield product
        hits = j['resultParams']['numHits']
        maxPage = hits//48 + 1
        category = response.meta['category']
        for page in range(2, maxPage + 1):
            url = self.base_api_url.format(categoryID=category, pageID=page)
            yield response.follow(url, callback=self.parseProductPage)
    
    def parseProductPage(self, response):
        j = json.loads(response.text)
        for product in self.parseProducts(j):
            yield product
    
    def parseProducts(self, j):
        for product in j['serviceProducts']:
            url = False
            for link in product['links']:
                url = link['href'] if link['rel'] == 'self' else False
            if url and 'name' in product:
                url = 'https://www.dm.de' + url
                request = scrapy.Request(url, callback=self.parseProduct)
                request.meta['productJSON'] = product
                yield request
    
    def getData(self, response=None, data=None):
        data = response.meta['productJSON']
        return data
    
    def getName(self, response=None, data=None):
        if data:
            if 'name' in data:
                return data['name']
        return None
    
    def getIngredients(self, response=None, data=None):
        ingredients = response.xpath('//dt[.="Zutaten"]/following-sibling::dd[1]')
        ingredients = ingredients.extract_first()
        if ingredients:
            ingredients = self.zutatensubRegEx.sub('', ingredients)
            ingredients = self.usualIngridientsSplitting(ingredients)
        return ingredients
    
    def getGtin(self, response=None, data=None):
        if 'gtin' in data:
            return data['gtin']
        else:
            return None
    
    def getBrand(self, response=None, data=None):
        if 'brand' in data:
            return data['brand']
        else:
            return None
    
    def getProducer(self, response=None, data=None):
        producer = response.xpath(
                '//dt[contains(., "Anschrift des Unternehmens")]/following-sibling::dd[1]'
                                    )
        producer = producer.extract_first()
        return producer
    
    def getSize(self, response=None, data=None):
        returnDict = dict()
        if 'netQuantityContent' in data:
            amount = data['netQuantityContent']
            returnDict['amount'] = amount
        if 'contentUnit' in data:
            unit = data['contentUnit']
            returnDict['unit'] = unit
        return returnDict
    
    def getPrice(self, response=None, data=None):
        returnDict = dict()
        if 'price' in data:
            amount = data['price']
            returnDict['amount'] = amount
        if 'priceCurrencyIso' in data:
            currency = data['priceCurrencyIso']
            returnDict['currency'] = currency
        return returnDict
    
    def getImageURL(self, response=None, data=None):
        image_tag = 'productimage'
        image_url = False
        if 'links' in data:
            for link in data['links']:
                if link['rel'][:len(image_tag)] == image_tag:
                    image_url = link['href']
                    break
        return image_url        