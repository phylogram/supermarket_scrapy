# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 14:21:22 2017

@author: Philip Röggla
"""
import re
import scrapy
import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider

class LebensmittelShopSpider(abstractShopSpider.AbstractShopSpider, scrapy.Spider):
    name = 'LebensmittelShop'
    start_urls = ['https://www.lebensmittel.de/?subd=0']
    store = 'Lebensmittel.de'
    
    productLinkXPATH = '//a[starts-with(@id, "detail_link")]/@href'
    mainCategoryLinkCSS = 'a.menuLink::attr(href)'
    getParamRegEx = re.compile('https:\/\/www\.lebensmittel\.de\/\?p=produktliste&CatLevel=1&subd=0&CatID=(\d+)')
    sizeRegEx = re.compile('(\d+)\s*([a-zA_Z])')
    productListLink = 'https://www.lebensmittel.de/?p=produktliste&MainCat=1&inFirstCatID=0&go=1&start={start}&end={end}&seite={page}&CatID={CatID}&oldCatID=-1&inCatID=0&form_Hersteller=&sortBy=&form_ProdsOnPage=100&form_PremiumFilter=-1&mode='
    productCountXPATH = '//span[@id="ProdCount"]/text()'
    gtinRegEx = re.compile('(\d{13})\D')
    priceAmountRegEx = re.compile('(\d+,{0,1}\d*)')
    biologischerAnbauRegEx = re.compile('aus kontrolliert biologischem anbau', flags=re.IGNORECASE)

    def __init__(self, *args, **kwargs):
        super(LebensmittelShopSpider, self).__init__(*args, **kwargs)
        self._setOUTPUT_()
    
    def parse(self, response):
        # get CategoryLinks        
        categoryLinks = response.css(self.mainCategoryLinkCSS)
        # call Page 1
        for categoryLink in categoryLinks:
            CatID = categoryLink.re_first(self.getParamRegEx)
            url = self.productListLink.format(start=0,
                                              end=101,
                                              page=0,
                                              CatID=CatID)
            request = scrapy.Request(url, callback=self.parseProductList)
            request.meta['CatID'] = CatID
            yield request

    def parseProductList(self, response):
        productLinks = response.xpath(self.productLinkXPATH).extract()
        if productLinks:
            for productLink in productLinks:
                productLink += '&reiter=1'
                yield response.follow(productLink,
                                      callback=self.preParseProduct
                                      )
        productCount = response.xpath(self.productCountXPATH).extract_first()
        productCount = int(productCount)
        CatID = response.meta['CatID']
        pages = productCount // 100
        for page in range(1, pages): # We have 0 allready
            start = page * 100 + 1
            end = (page + 1) * 100 + 1
            end = end if end < productCount else productCount
            url = self.productListLink.format(start=start,
                                              end=end,
                                              page=page,
                                              CatID=CatID)
            yield response.follow(url, callback=self.parseProducts)
    
    def parseProducts(self, response):
        productLinks = response.xpath(self.productLinkXPATH).extract()
        if productLinks:
            for productLink in productLinks:
                productLink += '&reiter=1'
                yield response.follow(productLink,
                                      callback=self.preParseProduct
                                      )  

    def preParseProduct(self, response):
        # chain requests / for this it is easier then selenium
        reiter = '&reiter=4'
        paramCut = len(reiter) * -1
        ajax = response.url[:paramCut] + reiter
        request = scrapy.Request(ajax, callback=self.parseProduct)
        request.meta['mainResponse'] = response.text
        yield request
        
    def getName(self, response=None, data=None):
        # We put this selector from the first response in a property
        # because this is the firast call with the second response
        # This is workaround ... ## To Do
        mainSelector = scrapy.Selector(text=response.meta['mainResponse'])
        self.mainSelector = mainSelector
        
        # Now we'll get the name ...
        name = response.xpath('//div[contains(./div/text(), "Produktbezeichnung")]')
        name = name.extract_first()
        return name

    def getIngredients(self, response=None, data=None):
        ingredients = response.css('div .enummerZutaten')
        ingredients = ingredients.extract_first()
        ingredients = re.sub(self.biologischerAnbauRegEx, ' ', ingredients)
        ingredients = self.usualIngridientsSplitting(ingredients)
        return ingredients

    def getLabels(self, response=None, data=None):
        '''This is overriden, because we have to search two responses'''
        labels = set()
        for label, search in self.labels.items():
            fM = self.mainSelector.re_first(search)
            fA = response.selector.re_first(search)
            found = label if fM or fA else None # if one or both positive -> found
            if found:
                labels.add(label)
        return list(labels)

    def getGtin(self, response=None, data=None):
        gtin = self.mainSelector.xpath('//meta[@name="keywords"]/@content')
        gtin = gtin.re_first(self.gtinRegEx)
        return gtin

    def getBrand(self, response=None, data=None):
        brand = self.mainSelector.xpath(
                    '//span[contains(., "Marke")]/following-sibling::span[1]/text()'
                                            )
        brand = brand.extract_first()
        return brand

    def getProducer(self, response=None, data=None):
        producer = self.mainSelector.xpath(
                '//span[contains(., "Hersteller")]/following-sibling::span[1]/text()'
                                            )
        producer = producer.extract_first()
        return producer
    
    def getSize(self, response=None, data=None):
        returnDict = dict()
        size = self.mainSelector.xpath(
                '//span[contains(., "Gewicht")]/following-sibling::span[1]/text()'
                                        )
        size = size.re(self.sizeRegEx)
        if len(size) == 2:
            amount, unit = size
            amount = amount.replace(',', '.')
            returnDict['amount'] = amount
            returnDict['unit'] = unit
        return returnDict

    def getPrice(self, response=None, data=None):
        returnDict = dict()
        priceAmount = self.mainSelector.xpath('//span[@id="ArtPreis"]')
        priceAmount = priceAmount.re_first(self.priceAmountRegEx)
        priceAmount = priceAmount.replace(',', '.')
        if priceAmount:
            returnDict['amount'] = priceAmount
            returnDict['currency'] = 'EUR' # it is € everytime
        return returnDict

    def getImageURL(self, response=None, data=None):
        imgURL = self.mainSelector.xpath('//img[@id="MainProdPic_pic"]/@src')
        imgURL = imgURL.extract_first()
        return imgURL