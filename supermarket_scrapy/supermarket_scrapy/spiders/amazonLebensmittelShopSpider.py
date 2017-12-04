# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 14:13:47 2017

@author: Philip Röggla

Needs: python: PIL.Image
Extern: tesseract with german language training set!
https://github.com/tesseract-ocr/tesseract/wiki
    set tesseractDataPath and tesseractExePath in properties!
"""
from io import BytesIO
import os
import re
import requests
import subprocess
import tempfile

from PIL import Image
import scrapy

import supermarket_scrapy.spiders.abstractShopSpider as abstractShopSpider

class AmazonLebensmittelShopSpider(abstractShopSpider.AbstractShopSpider, scrapy.Spider):
    name = 'AmazonLebensmittelShop'
    # This is the Food – Featured Categories node
    # As far as i understand it, alle food should be in this subcategory
    # Which provides a list of products with pagination
    start_urls = ['https://www.amazon.de/b?node=344162031']
    allowed_domains = ['amazon.de']
    store = ['amazon']

    tesseractDataPath = r'G:\Tesseract-OCR\tessdata'
    tesseractExePath = None # If None, command starts with tesseract:
    # cleanings tesseracts answer   
    ingridientRegexes = [
                re.compile('zutaten:([\s\w\"\%\!\,\.äüöß*]+)', re.IGNORECASE)
            ]
    ingredientsRegExCleaners = [
                re.compile('\s.*', re.DOTALL),
                re.compile('[\W]'),
            ]
    
    sizeRegEx = re.compile('(\d+?)\s+?([a-zA-Z]+)')
    priceRegEx = re.compile('([A-Z]{3})\s+?(\d+[\.,]{0,1}\d*)')
    
    def __init__(self, *args, **kwargs):
        super(AmazonLebensmittelShopSpider, self).__init__(*args, **kwargs)
        self._setOUTPUT_()
    
    
    def parse(self, response):
        resultList = response.css('ul.s-result-list')
        results = resultList.xpath('.//li')
        for result in results:
            link = result.xpath('.//a/@href').extract_first()
            yield response.follow(link, callback=self.parseProduct)
        nextLink = response.xpath('//a[@id="pagnNextLink"]/@href')
        nextLink = nextLink.extract_first()
        if nextLink:
            yield response.follow(nextLink, callback=self.parse)
    
    def getName(self, response=None, data=None):
        name = response.xpath('//span[@id="productTitle"]/text()')
        name = name.extract_first()
        return name
    
    def getIngredients(self, response=None, data=None):
        '''Ingredients only seem to be on pictures
        We download them temporarily and try to read
        their text with tesseract. If Zutaten: treat
        as ingredients ... 
        1) find pictures
        2) temp folder
        3) for each download with requests not scrapy
        4) read to file
        5) python read from file
        6) check with regex
        7) if yes break, procedd with normal cleansing
        '''
        
        #1 find pictures:    
        imgURLS = response.xpath('//div[@id="altImages"]//img/@src')
        imgURLS = imgURLS.extract()
        for imageURL in imgURLS:
            text = self.getTextFromPicture(imageURL)
            output = None
            for search in self.ingridientRegexes:
                found = search.findall(text)
                output = found[0] if found else None
            if output:
                break
        output = self.usualIngridientsSplitting(output)
        
        # Trying to get rid of false readings
        for cleaner in self.ingredientRegExCleaners():
            output = [re.sub(cleaner, '', element) for element in output]
        return output # and hope for the best
    
    # No GTIN on site, but there is the amaozon number, which is somehow convertable to 
    # to ean – I only found commercail services

    def getTextFromPicture(self, imageURL):
        imageRequest = requests.get(imageURL)
        img = Image.open(BytesIO(imageRequest.content))
        file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(file)
        outputFile = tempfile.NamedTemporaryFile(delete=False)
        tesseract = self.tesseractExePath if self.tesseractExePath else 'tesseract'
        process = subprocess.Popen([tesseract, file.name, outputFile.name, '-l', 'deu', '-tessdata-dir', self.tesseractDataPath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.communicate()
        with open(outputFile.name + '.txt', 'r') as handle:
            contents = handle.read()
        img.close()
        os.remove(file.name)
        os.remove(outputFile.name)
        os.remove(outputFile.name + 'txt')
        return contents
    
    def getBrand(self, response=None, data=None):
        brand = response.xpath('//a[@id="brand"]/text()')
        brand = brand.extract_first()
        return brand
    
    def getSize(self, response=None, data=None):
        returnDict = dict()
        size = response.xpath('//td[contains(@class, "label") and contains(., "Gewicht")]/following-sibling::td[contains(@class, "value")]/text()')
        size = size.re(self.sizeRegEx)
        if len(size) == 2:
            amount, unit = size
            # units are in fullname
            unit = unit.lower()
            if unit in self.units:
                unit = self.units[unit]
            returnDict['amount'] = amount
            returnDict[unit] = unit
        return returnDict
    
    def getPrice(self, response=None, data=None):
        returnDict = dict()
        price = response.xpath('//span[@id="priceblock_ourprice"]/text()')
        price = price.re(self.priceRegEx)
        if len(price) == 2:
            currency, amount = price
            returnDict['amount'] = amount
            returnDict['currency'] = currency
        return returnDict
    
    def getImageURL(self, response=None, data=None):
        imgURL = response.xpath('//img[@id="landingImage"]/@src')
        imgURL = imgURL.extract_first()
        return imgURL