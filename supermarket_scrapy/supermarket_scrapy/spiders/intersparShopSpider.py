#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 31 11:39:03 2017

Loads the first search page and finds the url of the api. The api url is not here, because I am not
sure if it's static. Goes through the api, takes data from the api and the provided urls and yields
next pages links.

@author: phylogram
"""
import json
import re
import scrapy
from scrapy.spiders import Spider
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider


class IntersparShop(abstractShopSpider.AbstractShopSpider, Spider):
    name = 'IntersparShop'
    start_urls = ['https://www.interspar.at/shop/lebensmittel/search/?sp_cs=UTF-8&q=*&rank=prod-rank&page=1']
    nextPageRegEx = re.compile('"next" : "(.+?)"')
    sizeRegEx = re.compile('(\d+?)\s*?([a-zA-Z]+)')
    store = ['Interspar']
    def __init__(self, *args, **kwargs):
        super(IntersparShop, self).__init__(*args, **kwargs)
        self._setOUTPUT_()

    def makeJSON(self, response):
        jsonString = re.findall('("results" :.*]).+?"applied-filters"',
                                response.text,  flags=re.DOTALL)
        if jsonString:
            jsonString = '{' + jsonString.pop() + '}'
            try:
                data = json.loads(jsonString)
                return data
            except Exception as e:
                print(e)
                return None
        else:
            return None

    def parse(self, response):
        """ Finds the url of the api at the search (anything) site """
        dataOptions = response.xpath('//input[@id="input_SearchBox"]/@data-options')
        dataOptions = dataOptions.extract_first()
        dataOptions = json.loads(dataOptions)
        self.APIurl = dataOptions['autocompleteUrl']
        if not self.APIurl.endswith('/'):
            self.APIurl += '/'
        yield response.follow(self.APIurl, callback=self.parseAPI)

    def parseAPI(self, response):
        """ Finds next page and products, which are passed """
        # Somehow the scrapy re module changes the result
        nextPage = re.search(self.nextPageRegEx, response.text)
        if nextPage:
            nextPage = nextPage.group(1)
            nextPage = nextPage[1:] if nextPage.startswith('/') else nextPage
            nextPage = self.APIurl + nextPage
            yield response.follow(nextPage, callback=self.parseAPI)
        data = self.makeJSON(response)
        if 'results' in data:
            results = data['results']
            for result in results:
                if 'disruptive-code' in result:
                    disruptiveCode = result['disruptive-code']
                    productLink = 'https://www.interspar.at/shop/lebensmittel/AllProducts/p/' + str(disruptiveCode)
                    request = scrapy.Request(productLink, callback=self.parseProduct, meta=result)
                    yield request

    def getData(self, response=None, data=None):
        return response.meta

    def getName(self, response=None, data=None):
        if 'product-short-description-2' in data:
            name = data['product-short-description-2']
            return name
        else:
            return None

    def getIngredients(self, response=None, data=None):
        ingredients = response.css('.ingredientInformation li.desc')
        ingredients = ingredients.extract_first()
        if ingredients:
            if 'Zutaten' in ingredients:
                ingredients = self.usualIngridientsSplitting(ingredients)
            else:
                ingredients = None
        return ingredients

    def getBrand(self, response=None, data=None):
        if 'title' in data:
            return data['title']
        else:
            return None

    def getProducer(self, response=None, data=None):
        producer = response.css('.contactInformation li.desc')
        producer = producer.extract_first()
        return producer

    def getCategory(self, response=None, data=None):
        category = response.xpath('//div[@id="breadcrumb"]//li/a/text()')
        category = category.extract()
        if len(category) >= 5:
            category = category[-2]
        elif len(category) == 3:
            category = category[-1]
        else:
            category = None
        return category

    def getSize(self, response=None, data=None):
        returnDict = dict()
        if 'product-short-description-3' in data:
            size = data['product-short-description-3']
            size = re.findall(self.sizeRegEx, size)
            if size and len(size[0]) == 2:
                amount, unit = size[0]
                unit = unit.lower()
                if unit in self.units:
                    unit = self.units[unit]
                if unit not in self.units.values():
                    return None
                returnDict['amount'] = amount
                returnDict['unit'] = unit
        return returnDict

    def getPrice(self, response=None, data=None):
        returnDict = dict()
        if 'product-regularprice' in data:
            amount = data['product-regularprice']
            returnDict['amount'] = amount
            returnDict['currency'] = 'EUR'

    def getImageURL(self, response=None, data=None):
        if 'product-image' in data:
            return data['product-image']
        else:
            return None
