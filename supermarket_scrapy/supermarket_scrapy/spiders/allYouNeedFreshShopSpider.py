# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 17:35:20 2017

@author: Philip Röggla

Needs: Downloader Middleware: 'supermarket_scrapy.middlewares.UseChromePostalCodes'
"""
import json
import re
import time
import scrapy
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider

class AllYouNeedFreshShopSpider(abstractShopSpider.AbstractShopSpider, scrapy.Spider):
    name = 'AllYouNeedFresh'
    store = 'allyouneedfresh'
    allowed_domains = ['allyouneedfresh.de']
    base_url = 'https://www.allyouneedfresh.de/'
    start_url = 'https://www.allyouneedfresh.de/alle_kategorien' # this is no typo! See def start_requests
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

    visited = {}
    allowedVisits = 10
    parsedProducts = {}
    
    dataRegEx = re.compile('^\{"name.+')
    ingredientsRegEx = re.compile('<strong>Zutaten:<\/strong><br>(.+?)<br>')
    sizeRegEx = re.compile('.+?,\s+(\d+[,\.]{0,1}\d*)\s+(\w+)')
    
    def __init__(self, *args, **kwargs):
        super(AllYouNeedFreshShopSpider, self).__init__(*args, **kwargs)
        self._setOUTPUT_()

    def start_requests(self):
        for plz in self.mainPLZ.values():
            request = scrapy.Request(self.start_url, callback=self.parse,
                                     meta={'plz':plz}, dont_filter=True) # !!!
            yield request

    def parse(self, response):
        plz = response.meta['plz']
        menuLinks = response.xpath('//span[@class="categoryItem secondLevel"]/a/@href')
        menuLinks = menuLinks.extract()
        for menuLink in menuLinks:
           menuLink = self.base_url + menuLink
           thisTime = time.strftime('%d-%m-%Y-%H:%M')
           if menuLink in self.visited:
               self.visited[menuLink] += 1
               message = '''{time}\n
                           PLZ {plz}\n
                           MenuLink allready visited: \n
                           \t {url} \n
                           \t {number} - times\n
                           '''.format(time=thisTime, plz=plz,
                                       url=menuLink, 
                                       number=self.visited[menuLink])
               self.logger.debug(message)
           else:
               self.visited[menuLink] = 1
               message = '''{time}\n
                           PLZ {plz}\n
                           MenuLink first visit: \n
                           \t {url} \n
                           '''.format(time=thisTime, plz=plz, url=menuLink)
               self.logger.debug(message)
           if self.visited[menuLink] <= self.allowedVisits:
               request = scrapy.Request(menuLink,
                                        callback=self.parseCategory,
                                        dont_filter=True # !!!
                                        )                   
               request.meta['plz'] = plz
               yield request
           else:
               message = '''XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n
                           {time}\n
                           PLZ {plz}\n
                           MenuLink visited one too much: \n
                           \t {url} \n
                           \t {number} - times\n
                           XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n
                           '''.format(time=thisTime, plz=plz, url=menuLink,
                                       number=self.visited[menuLink])
               self.logger.debug(message)                   
                         
    def parseCategory(self, response):
        plz = response.meta['plz']
        productLinks = response.xpath('//a[contains(@class, "article-link")]/@href')
        productLinks = productLinks.extract()
        for productLink in productLinks:
            productLink = self.base_url + productLink
            if productLink not in self.parsedProducts:
                self.parsedProducts[productLink] = 1
                request = scrapy.Request(productLink,
                                            callback=self.parseProduct,
                                            dont_filter=True # !!!
                                            )
                request.meta['plz'] = plz
                yield request
                thisTime = time.strftime('%d-%m-%Y-%H:%M')
                message = '''°°°°°°°°°°°°°°°°°°°°\n
                             {time}\n
                             PLZ {plz}\n
                             Product visit 1: \n
                             \t {url} \n
                             °°°°°°°°°°°°°°°°°°°°\n
                             '''.format(time=thisTime, plz=plz, url=productLink)
                             
                self.logger.debug(message)
            else:
                # Yes – I am afraid of infenite crawling loops!
                message = '''$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n
                             %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n
                             {time}\n
                             PLZ {plz}\n
                             Product allready visited: \n
                             \t {url} \n
                             \t {number} times\n
                             %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n
                             $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n
                             '''.format(time=thisTime, plz=plz, url=productLink, 
                                 number=self.parsedProducts[productLink])
                self.logger.debug(message)
                self.parsedProducts[productLink] += 1
                
     
    def getData(self, response=None, data=None):
        data = response.xpath('//script[@type="application/ld+json"]/text()')
        data = data.re_first(self.dataRegEx)
        if data:
            data = json.loads(data)
            return data
        else:
            return None

    def getName(self, response=None, data=None):
        if data:
            if 'name' in data:
                return data['name']
        return None

    def getIngredients(self, response=None, data=None):
        ingredients = response.css('.product-db-details')
        ingredients = ingredients.xpath('.//p')
        ingredients = ingredients.re_first(self.ingredientsRegEx)
        if ingredients:
            ingredients = ingredients.replace(' nach Fairtrade-Standards gehandelt', '')
            ingredients = self.usualIngridientsSplitting(ingredients)
        return ingredients

    def getGtin(self, response=None, data=None):
        if 'gtin8' in data:
            return data['gtin8']

    def getBrand(self, response=None, data=None):
        if 'brand' in data:
            if 'name' in data['brand']:
                return data['data']['brand']
        return None

    def getSize(self, response=None, data=None):
        returnDict = dict()
        if 'name' in data:
            size = re.findall(self.sizeRegEx, data['name'])
            if len(size) == 2:
                amount, unit = size
                returnDict['amount'] = amount
                returnDict['unit'] = unit
        return returnDict

    def getPrice(self, response=None, data=None):
        returnDict = dict()
        if 'offers' in data:
            if 'price' in data['offers']:
                returnDict['amount'] = data['offers']['price']
            if 'currency' in data['offers']:
                returnDict['currency'] = data['offers']['currency']
        return returnDict

    def getImageURL(self, response=None, data=None):
        if 'image' in data:
            image = data['image']
            return image