# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 11:16:21 2017

@author: Philip Röggla
A generic spider for all other shop spiders. This is not a real spider, and not
a real abstract class. It just bundles some utilities
"""

import codecs
import html
import os
import re
import time

import supermarket_scrapy.labels

class AbstractShopSpider():
    store = None
    name = None
    labels = supermarket_scrapy.labels.labels
    listOutputDirectory = '.'
    
    whiteSpaceRegEx = re.compile('[\s]')
    htmlTagRegEx = re.compile('<\/*?\w.+?>')
    
    decimalSepRegEx = re.compile('(?<=\d),(?=\d)')
    splitIngredientsRegEx = re.compile(',\s*(?![^()]*\))')
    #there is a german unit -> abbrevation dictionary as property at the end of the class
    
    def _setOUTPUT_(self):  
        self.ressourcesOUTPUT = set()
        self.labelsOUTPUT = set()
        self.brandsOUTPUT = set()

    
    def parseProduct(self, response):
        ''''parses Products as schema.json - the actual parsing functions will be
        overriden in the spider subclasses'''
        
        parsedDict = dict()
        data = self.getData(response)
        name = self.getName(response=response,data=data)
        if name:
            parsedDict['name'] = self.cleanString(name)
        else:
            return None
        ingredients = self.getIngredients(response=response,data=data)
        if ingredients:
            for ingredient in ingredients:
                self.ressourcesOUTPUT.add(ingredient)
            parsedDict['ingredients'] = ingredients
        else:
            parsedDict['ingredients'] = []
            self.logger.critical('No ingridients at '+ response.url)
        productLabels = self.getLabels(response=response,data=data)
        if productLabels:
            parsedDict['labels'] = productLabels
            for label in productLabels:
                self.labelsOUTPUT.add(label)
        else:
            parsedDict['labels'] = []
        store = self.getStores(response=response,data=data)
        if store:
            parsedDict['stores'] = store
        gtin = self.getGtin(response=response,data=data)
        if gtin:
            parsedDict['gtin'] = self.cleanString(gtin)
        brand = self.getBrand(response=response,data=data)
        if brand:
            brand = self.cleanString(brand)
            self.brandsOUTPUT.add(brand)
            parsedDict['brand'] = brand
        producer = self.getProducer(response=response,data=data)
        if producer:
            parsedDict['producer'] = self.cleanString(producer)
        category = self.getCategory(response=response,data=data)
        if category:
            parsedDict['category'] = self.cleanString(category)
            
        parsedDict['details'] = dict()
        size = self.getSize(response=response,data=data)
        if size:
            parsedDict['details']['size'] = dict()
            if 'amount' in size:
                amount = size['amount']
                if amount:
                    amount = self.cleanString(amount)
                    amount = float(amount)
                    parsedDict['details']['size']['amount'] = amount
            if 'unit' in size:
                    unit = size['unit']
                    if unit:
                        unit = self.cleanString()
                        parsedDict['details']['size']['unit'] = unit
                
        price = self.getPrice(response=response,data=data)
        if price:
           parsedDict['details']['price'] = dict()
           if 'amount' in price:
                   amount = price['amount']
                   if amount:
                       amount = self.cleanString(amount)
                       amount = float(amount)
                       parsedDict['details']['price']['amount'] = amount
           if 'currency' in price:
               currency = price['currency']
               if currency:
                   currency = self.cleanString(currency)
                   parsedDict['details']['price']['currency'] = currency
               
        imageURL = self.getImageURL(response=response,data=data)
        if imageURL:
            parsedDict['details']['image_url'] = imageURL.strip()
        
        yield parsedDict
     
        
    # Dummy get data methods
    # All of them get self, response and data    
    def getData(self, response=None, data=None):
        'Any structured data parts from the website'
        return None
    def getName(self, response=None, data=None):
        return None
    def getIngredients(self, response=None, data=None):
        return None
    def getLabels(self, response=None, data=None):
        'searches for labels with regex. If override, please check for unique lists as out'
        labels = set()
        for label, search in self.labels.items():
            found = response.selector.re_first(search)
            if found:
                labels.add(label)
        return list(labels)
    def getStores(self, response=None, data=None):
        if type(self.store) == str:
            return [self.store]
        elif type(self.store) == list:
            return self.store
    def getGtin(self, response=None, data=None):
        return None
    def getBrand(self, response=None, data=None):
        return None
    def getProducer(self, response=None, data=None):
        return None
    def getCategory(self, response=None, data=None):
        return None
    def getSize(self, response=None, data=None):
        'return dict with amount and or unit or None!'
        return None
    def getPrice(self, response=None, data=None):
        'return dict with amount and or unit or None!'
        return None
    def getImageURL(self, response=None, data=None):
        return None
    
    # usual methods for all subchilds
    def usualIngridientsSplitting(self, ingredientString):
        '''The most typical ingredients splitting and cleaning.
        use in getIngredients and try to get rid of special phrases before.
        '''
        if not ingredientString:
            return None
        else:
            ingredientString = str(ingredientString)
            ingredients = ingredientString.replace('*', '')
            ingredients = re.sub(self.whiteSpaceRegEx, ' ', ingredients)
            ingredients = self.decimalSepRegEx.sub('.', ingredients)
            ingredients = re.sub(self.htmlTagRegEx,'', ingredients) # get rid of html tags
                                                    # only works if not broken!
            ingredients = html.unescape(ingredients)
            ingredients = re.split(self.splitIngredientsRegEx, ingredients)
            ingredients = [element.strip() for element in ingredients]
            # getting rid of unwanted dots at the end To Do
            ingredients = list(set(ingredients)) # make them unique
            ingredients = list(filter(None, ingredients)) # delete empty items
            return ingredients
    
    def cleanString(self, string):
        'Cleans Strings - html, utf-8 encoding ... '
        if not string:
            return None
        string = str(string)
        string = re.sub(self.whiteSpaceRegEx, ' ', string)
        string = html.unescape(string)
        string = re.sub(self.htmlTagRegEx, '', string)
        string = codecs.encode(string)
        string = codecs.decode(string, encoding='utf-8', errors='namereplace')
        string = string.strip()
        return string       
        
    def closed(self, message):
        directory = self.listOutputDirectory + os.sep
        thisTime = time.strftime('%d-%m-%Y_%H-%M')
        brandsFileName = directory + '_'.join([self.name, 'brand', thisTime]) + '.txt'
        ressourcesFileName = directory + '_'.join([self.name, 'ressources', thisTime]) + '.txt'
        labelsFileName = directory + '_'.join([self.name, 'labels', thisTime]) + '.txt'
        
        with codecs.open(brandsFileName, mode='w',encoding='utf-8', errors='namereplace') as file:
            file.write('\n'.join(self.brandsOUTPUT))
        with codecs.open(ressourcesFileName, mode='w', encoding='utf-8', errors='namereplace') as file:
            file.write('\n'.join(self.ressourcesOUTPUT))
        with codecs.open(labelsFileName, mode='w', encoding='utf-8', errors='namereplace') as file:
            file.write('\n'.join(self.labelsOUTPUT))
    
    
    units = {           
            #zeitmaße
            "stunde": "h",
            "minute": "min",
            "sekunde": "s",
            #längenmaße
            "kilometer": "km",
            "hektometer": "hm",
            "dekameter": "dam",
            "meter": "m",
            "dezimeter": "dm",
            "zentimeter": "cm",
            "millimeter": "mm",
            #flächenmaße
            "quadratkilometer": "km2",
            "hektar": "ha",
            "ar": "a",
            "quadratmeter": "m2",
            "quadratdezimeter": "dm2",
            "quadratzentimeter": 	"cm2",
            "quadratmillimeter": "mm2",
            #raummaße
            "bruttoraumzahl": "brz",
            "bruttoregistertonne": "brt",
            "kubikmeter": "m3",
            "kubikdezimeter": "dm3",
            "kubikzentimeter": "cm3",
            "kubikmillimeter": "mm3",
            #hohlmaße
            "hektoliter": "hl",
            "dekaliter": "dal",
            "liter": "l",
            "deziliter": "dl",
            "zentiliter": "cl",
            "milliliter": "ml",
            #masseeinheiten
            "tonne": "t",
            "zentner": "ztr",
            "kilogramm": "kg",
            "hektogramm": "hg",
            "gramm": "g",
            "dezigramm": "dg",
            "zentigramm": "cg",
            "milligramm": "mg",            
            }