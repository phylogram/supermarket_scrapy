#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 30 22:07:31 2017

@author: phylogram
"""
from itertools import count
import re
from scrapy.spiders import Spider
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider


class MpreisShop(abstractShopSpider.AbstractShopSpider, Spider):
    name = 'mpreisShop'
    store = 'mpreis'
    start_urls = ['https://shop.mpreis.at/Lebensmittel/',
                  'https://shop.mpreis.at/Getraenke/',
                  'https://shop.mpreis.at/Drogeriemarkt/',
                  ]
    pageRegEx = re.compile('(\d+?/$)')
    sizeAmountRegEx = re.compile('\d+[,]*\d*')
    priceAmountRegEx = re.compile('(\d+?)\D')

    maxPagePerCategory = 10**3  # Security net

    def __init__(self, *args, **kwargs):
        super(MpreisShop, self).__init__(*args, **kwargs)
        self._setOUTPUT_()

    def parse(self, response):
        productLinks = response.css('a.tm-lnk-block::attr(href)')
        for productLink in productLinks:
            yield response.follow(productLink, self.parseProduct)
        page = count(2)
        nextButton = response.xpath('//button[@id="continous-scroll"]')
        redirected = 'redirect_urls' in response.meta
        while nextButton or not redirected:
            pageNumber = next(page)
            url = re.sub(self.pageRegEx, '', response.url)
            url += str(pageNumber) + '/'
            yield response.follow(url)
            if pageNumber > self.maxPagePerCategory:
                break
            nextButton = response.xpath('//button[@id="continous-scroll"]')
            redirected = 'redirect_urls' in response.meta

    def getName(self, response=None, data=None):
        name = response.xpath('//h1[@id="productTitle"]/span/text()')
        name = name.extract_first()
        return name

    def getIngredients(self, response=None, data=None):
        ingredients = response.xpath('//th[.="Zutaten"]/following-sibling::td')
        ingredients = ingredients.extract_first()
        if ingredients:
            ingredients = self.usualIngridientsSplitting(ingredients)
        return ingredients

    def getBrand(self, response=None, data=None):
        brand = response.xpath('//th[.="Marke"]/following-sibling::td')
        brand = brand.extract_first()
        return brand

    def getCategory(self, response=None, data=None):
        category = response.xpath('//ol[@id="breadcrumb"]/li/a/text()')
        category = category.extract()
        if category:
            category = category.pop()
        return category

    def getSize(self, response=None, data=None):
        returnDict = dict()
        size = response.xpath('//div[@class="tm-content"]/text()')
        size = size.extract_first()
        size = size.strip()
        size = size.split()
        if len(size) < 2:
            return None
        size = size[:2]
        m = re.match(self.sizeAmountRegEx, size[0])
        if m:
            s = m.group()
            s = re.sub(self.decimalSepRegEx, '.', s)
            s = float(s)
            returnDict['amount'] = s
        unit = size[1].lower()
        if unit in self.units:
            unit = self.units[unit]
        if unit not in self.units.values():
            return None
        returnDict['unit'] = unit
        return returnDict

    def getPrice(self, response=None, data=None):
        returnDict = dict()
        xp = '//label[@id="productPrice"]'
        price = response.xpath(xp)
        amount = price.re(self.priceAmountRegEx)
        if len(amount) <= 2:
            amount = '.'.join(amount)
            returnDict['amount'] = amount
        else:
            return None
        price = price.extract_first()
        if price and '€' in price:
            returnDict['currency'] = 'EUR'
        return returnDict

    def getImageURL(self, response=None, data=None):
        imgURL = response.xpath('//img[@itemprop="image"]/@src')
        imgURL = imgURL.extract_first()
        return imgURL
