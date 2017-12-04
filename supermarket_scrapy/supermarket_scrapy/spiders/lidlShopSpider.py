# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 19:36:28 2017

@author: Philip Röggla

Sometimes no responses to requests - does not seem to have a pattern
I crawled the whole page with no delay and it did not have any effect.

And more: This site is not well structured – for robots or anybody else
I retrieve the brand, id and some more informatin from a json in the script

Labels are just anywhere in the text, not explicitly named, and can not be
found by html structure.
There just came one solution to my mind: Load all known labels, compile them as
regex and search every site for it. 
"""
import json
import re
from scrapy.spiders import SitemapSpider
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider

class LidlShopSpider(abstractShopSpider.AbstractShopSpider, SitemapSpider):
    name = 'LidlShop'
    store = ['Lidl']
    
    sitemap_urls = ['https://www.lidl.de/robots.txt'] # will lead to sitemap 
    sitemap_follow =  [re.compile('product', flags=re.IGNORECASE)]
    
    selectScriptXPath = 'body/script[1]/text()'
    scriptSelectRegEx = re.compile('dataLayer\.push.*products\":\[(.*)\]')

    zutatenRegEx = re.compile('<b>Zutaten:<br><\/b>(.+?)<\/div>')
    decDelimiterRegEx = re.compile('(?<=\d),(?=\d)')
    sizeAmountRegEx = re.compile('\d+.\d+')
    sizeUnitRegEx = re.compile('\d+.\d+-(\w)')
    
    def __init__(self, *args, **kwargs):
        super(LidlShopSpider, self).__init__(*args, **kwargs)
        self._setOUTPUT_()    
    
    def parse(self, response):
        for product in self.parseProduct(response):
            yield product
        
    def getData(self, response=None, data=None):
        script = response.xpath(self.selectScriptXPath)
        jstring = script.re_first(self.scriptSelectRegEx)
        if not jstring:
            self.logger.info('No desired script json at ' + response.url)
            return None # There is nothing to parse 
        jdict = json.loads(jstring)
        return jdict
    
    def getName(self, response=None, data=None):
        if 'name' in data:
            return data['name']
        else:
            return None
    
    def getIngredients(self, response=None, data=None):
        ingredients = response.xpath('//div[@id="Produktinformationen"]')
        ingredients = ingredients.re_first(self.zutatenRegEx)
        ingredients = self.usualIngridientsSplitting(ingredients)
        return ingredients
    
    def getBrand(self, response=None, data=None):
        if 'brand' in data:
            return data['brand']
        else:
            None
    
    def getCategory(self, response=None, data=None):
        if 'category' in data:
            category = data['category']
            category = category.split('/') #split category/subcategory
            category = category[0] # only top level category
            category = category.lower()
            return category
        else:
            return None
        
    def getSize(self, response=None, data=None):
        returnDict = dict()
        amountstring = response.xpath(
                '//div[@id="articledetail"]//small[@class="amount"]/text()'
                                        )
        if amountstring:
            amount = amountstring.re_first(self.sizeAmountRegEx)
            if amount:
                returnDict['amount'] = amount

            unit = amountstring.re_first(self.sizeUnitRegEx)
            if unit:
                returnDict['unit'] = unit
        return returnDict
    
    def getPrice(self, response=None, data=None):
        returnDict = dict()
        if 'price' in data:
            returnDict['amount'] = data['price']
            # there is an all prices in Euro policy at Lidl
            returnDict['currency'] = 'EUR'
    
    def getImageURL(self, response=None, data=None):
        imageURL = response.xpath(
  './/img[contains(@src, "product") and not(contains(@src, "tinythumbnail"))]'
                                      )
        imageURL = imageURL.extract_first()
        return imageURL
 