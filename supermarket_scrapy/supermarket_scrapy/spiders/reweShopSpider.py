# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 18:05:35 2017

@author: Philip Röggla

Needs: Downloader middleware: 'supermarket_scrapy.middlewares.UseChromePostalCodes'
Needs: Selenium Chrome


Workflow:
    Go to main page
    For each PLZ:
        for each store/delivery:
            recieve cookie
            go to all products:
                go through all subsites ?n until "no products"
            delete cookie
"""
import json
import re
import time
import scrapy
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider

class ReweShopSider(abstractShopSpider.AbstractShopSpider, scrapy.Spider):
    name = 'ReweShop'
    # Rewe wants post codes - there is the need for some human preselection:
    # compare:
    # http://www.stepmap.de/karte/logistik-standorte-rewe-logistik-1431334
    # We said 10 - but this make far too many requests, instead here 4
    mainPLZ = { 'Dresden': '01067',
                'Berlin': '10115',
                'Hamburg': '20095',
                #'Hannover': '30159',
                #'Düsseldorf': '40210',
                #'Köln': '50667',
                #'Frankfurt am Main': '60306',
                #'Stuttgart': '70173',
                'München': '80331',
                #'Nürnberg': '90402'
            }
    start_url = 'https://shop.rewe.de/productList' # this is no typo! See def start_requests
    baseURL = 'https://shop.rewe.de'

    sizeRegEx = re.compile('(\d+?)([a-zA-Z]+)')
    ingredientReplacements = [
                'aus Fairem Handel',
                'aus Fairem Handel,',
                'aus kontrolliert ökologischem Anbau',
                'aus kontrolliert ökologischem Anbau,',
            ]

    visited = {}
    allowedVisits = 10
    parsedProducts = []
    store = 'Rewe'
    
    def __init__(self, *args, **kwargs):
        super(ReweShopSider, self).__init__(*args, **kwargs)
        self._setOUTPUT_()
    def start_requests(self):
        for plz in self.mainPLZ.values():
            request = scrapy.Request(self.start_url + '?page=1', callback=self.parse,
                                     meta={'plz':plz}, dont_filter=True) # !!!
            yield request

    def parse(self, response):
        plz = response.meta['plz']

        nextLink = response.css('a.MainTypeCompMolePagiPaginationLinkNext::attr(href)')
        nextLink = nextLink.extract_first()
        if nextLink:
            nextLink = self.start_url + nextLink
            thisTime = time.strftime('%d-%m-%Y-%H:%M')
            if nextLink in self.visited:
                self.visited[nextLink] += 1
                message = '''{time}\n
                           PLZ {plz}\n
                           MenuLink allready visited: \n
                           \t {url} \n
                           \t {number} - times\n
                           '''.format(time=thisTime, plz=plz,
                                       url=nextLink,
                                       number=self.visited[nextLink])

            else:
               self.visited[nextLink] = 1
               message = '''{time}\n
               PLZ {plz}\n
               MenuLink first visit: \n
               \t {url} \n
               '''.format(time=thisTime, plz=plz, url=nextLink)

            self.logger.debug(message)

            if self.visited[nextLink] <= self.allowedVisits:
                request = scrapy.Request(nextLink, callback=self.parse,
                                     meta={'plz':plz}, dont_filter=True) # !!!

                yield request

        productLinks = response.css('div.MainTypeCompOrgaProdProductTileContent a::attr(href)')
        productLinks = productLinks.extract()
        for productLink in productLinks:
            productLink = self.baseURL + productLink
            if productLink not in self.parsedProducts:
                request = scrapy.Request(productLink, callback=self.parseProduct,
                                         meta={'plz':plz}, dont_filter=True) # !!!
                yield request
                self.parsedProducts.append(productLink)

    def getData(self, response=None, data=None):
        data = response.xpath('//script[@type="application/ld+json"]/text()')
        data = data.extract_first()
        if data:
            data = json.loads(data)
        return data

    def getName(self, response=None, data=None):
        if data:
            if 'name' in data:
                return data['name']
        return None

    def getIngredients(self, response=None, data=None):
        ingredientString = response.xpath('//h3[contains(., "Zutaten:")]/parent::div/text()')
        ingredientString = ingredientString.extract_first()
        if ingredientString:
            ingredientString.replace('°', '')
            for replace in self.ingredientReplacements:
                ingredientString.replace(replace, '')
            ingredientString = self.usualIngridientsSplitting(ingredientString)
        return ingredientString

    def getGtin(self, response=None, data=None):
        if 'gtin13' in data:
            return data['gtin13']
        else:
            return None

    def getBrand(self, response=None, data=None):
        if 'brand' in data:
            if 'name' in data:
                return data['brand']['name']
        return None

    def getProducer(self, response=None, data=None):
        producer = response.xpath('//h3[contains(., "Kontaktname")]/parent::div/text()')
        producer = producer.extract_first()
        return producer

    def getCategory(self, response=None, data=None):
        category = response.css('.lr-breadcrumbs__link')
        category = category.extract()
        if category:
            if len(category) >= 2:
                category = category[1]
            else:
                category = category[0]
        return category

    def getSize(self, response=None, data=None):
        returnDict = dict()
        h1 = response.xpath('//h1/text()')
        size = h1.re(self.sizeRegEx)
        if len(size) == 2:
            amount, unit = size
            unit = unit.lower()
            if unit in self.units:
                unit = self.units[unit]
            returnDict['amount'] = amount
            returnDict['unit'] = unit
        return returnDict

    def getPrice(self, response=None, data=None):
        returnDict= dict()
        if 'offers' in data:
            if 'price' in data['offers']:
                returnDict['amount'] = data['offers']['price']
            if 'priceCurrency' in data['offers']:
                returnDict['currency'] = data['offers']['priceCurrency']
        return returnDict

    def getImageURL(self, response=None, data=None):
        if 'image' in data:
            return data['image']
