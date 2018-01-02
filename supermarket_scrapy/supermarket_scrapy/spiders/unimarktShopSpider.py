#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 30 20:32:01 2017

@author: phylogram
"""
import re
from scrapy.spiders import Spider
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider


class UnimarktShopSpider(abstractShopSpider.AbstractShopSpider, Spider):
    name = 'UnimarktShop'
    store = 'Unimarkt'
    start_urls = ['https://shop.unimarkt.at/']
    categories = ['milchprodukte', 'obst-gemuese', 'fleisch-wurst',
                  'getraenke', 'lebensmittel', 'suesses-snacks',
                  'brot-gebaeck', 'tiefkuehl']
    sizeRegEx = re.compile('(\d+?)\s*?([a-zA-Z]+?)')

    def __init__(self, *args, **kwargs):
        super(UnimarktShopSpider, self).__init__(*args, **kwargs)
        self._setOUTPUT_()

    def parse(self, response):
        links = response.xpath('//a[@class="dropdown-toggle"]/@href')
        for link in links:
            category = link.extract()
            category = category[1:]
            if category not in self.categories:
                continue
            else:
                yield response.follow(link, callback=self.parseCategory)

    def parseCategory(self, response):
        links = response.xpath('//div[@class="dragItem produktContainer"]/div[@class="image"]/a/@href')
        for link in links:
            yield response.follow(link, callback=self.parseProduct)

    def getName(self, response=None, data=None):
        name = response.xpath('//h1[@itemprop="name"]/text()')
        name = name.extract_first()
        return name

    def getIngredients(self, response=None, data=None):
        ingredients = response.xpath('//h5[.="Zutatenliste: "]/following-sibling::p/text()')
        ingredients = ingredients.extract_first()
        if ingredients:
            ingredients = self.usualIngridientsSplitting(ingredients)
        return ingredients

    def getBrand(self, response=None, data=None):
        brand = response.xpath(
            '//h5[starts-with(.,"Marke / Submarke:")]/following::p[@class="fieldValue"][1]/text()'
                                )
        brand = brand.extract_first()

    def getProducer(self, response=None, data=None):
        producer = response.xpath(
                    '//h5[.="Kontakt: Name Inverkehrbringer: "]/following-sibling::p/text()'
                                    )
        producer = producer.extract_first()
        return producer

    def getCategory(self, response=None, data=None):
        breadcrumbs = response.css('.breadcrumb')
        breadcrumbs = breadcrumbs.xpath('.//a[@itemprop="item"]/span/text()')
        breadcrumbs = breadcrumbs.extract_first()
        return breadcrumbs

    def getSize(self, response=None, data=None):
        returnDict = dict()
        size = response.css('.desc')
        size = size.xpath('./h3/text()')
        size = size.re(self.sizeRegEx)
        if len(size) == 2:
            amount, unit = size
            unit = str(unit)
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
        price = response.xpath('//meta[@itemprop="price"]/@content')
        price = price.extract_first()
        if price:
            returnDict['amount'] = price
        currency = response.xpath('//meta[@itemprop="priceCurrency"]/@content')
        currency = currency.extract_first()
        if currency:
            returnDict['currency'] = currency
        return returnDict

    def getImageURL(self, response=None, data=None):
        img = response.xpath('//div[@id="artikelDetailSlider"]')
        imgURL = img.css('img.magnifier::attr(src)')
        imgURL = imgURL.extract_first()
        if imgURL:
            imgURL = self.start_urls[0] + imgURL[1:]  # Get rid of starting /
        return imgURL
