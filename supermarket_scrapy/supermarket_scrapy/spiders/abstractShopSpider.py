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


import supermarket_scrapy. labels as labels
import supermarket_scrapy.cleanString as cleanString
class AbstractShopSpider():
    store = None
    name = None
    labels = labels.labels
    listOutputDirectory = '/media/phylogram/Programme/moreOnion/supermarktScrapy/newData/mapping/'

    whiteSpaceRegEx = re.compile('[\s]+')
    htmlTagRegEx = re.compile('(<\/{0,1}\w.*?>)')
    decimalSepRegEx = re.compile('(?<=\d),(?=\d)')
    splitIngredientsRegEx = re.compile(',\s*(?![^()]*\))')
    kannSpurenRegEx = re.compile('Kann .+? enthalten')
    delNoneDecDotsRegEx = re.compile('(?<!\d)\.(?!\d)')
    footnoteRegEx = re.compile('[\*°]\s*?aus.+')
    zutatenRegEx = re.compile('zutaten:', re.IGNORECASE)
    beforeColonRegEx = re.compile('[a-zA-Z]+?:')
    # there is a german unit
    units = cleanString.units


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
            parsedDict['name'] = cleanString.cleanString(name)
        else:
            self.logger.critical('No name ' + response.url)
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
        store = self.getStores(response=response, data=data)
        if store:
            parsedDict['stores'] = store
        gtin = self.getGtin(response=response, data=data)
        if gtin:
            parsedDict['gtin'] = cleanString.cleanString(gtin)
        brand = self.getBrand(response=response,data=data)
        if brand:
            brand = cleanString.cleanString(brand)
            self.brandsOUTPUT.add(brand)
            parsedDict['brand'] = brand
        producer = self.getProducer(response=response,data=data)
        if producer:
            parsedDict['producer'] = cleanString.cleanString(producer)
        category = self.getCategory(response=response,data=data)
        if category:
            parsedDict['category'] = cleanString.cleanString(category)

        parsedDict['details'] = dict()
        size = self.getSize(response=response,data=data)
        if size:
            parsedDict['details']['size'] = dict()
            if 'amount' in size:
                amount = size['amount']
                if amount:
                    amount = cleanString.cleanString(amount)
                    amount = re.sub(self.decimalSepRegEx, '.', amount)
                    amount = float(amount)
                    parsedDict['details']['size']['amount'] = amount
            if 'unit' in size:
                    unit = size['unit']
                    if unit:
                        unit = cleanString.cleanString(unit)
                        parsedDict['details']['size']['unit'] = unit

        price = self.getPrice(response=response,data=data)
        if price:
           parsedDict['details']['price'] = dict()
           if 'amount' in price:
                   amount = price['amount']
                   if amount:
                       amount = cleanString.cleanString(amount)
                       amount = re.sub(self.decimalSepRegEx, '.', amount)
                       amount = float(amount)
                       parsedDict['details']['price']['amount'] = amount
           if 'currency' in price:
               currency = price['currency']
               if currency:
                   currency = cleanString.cleanString(currency)
                   parsedDict['details']['price']['currency'] = currency
        parsedDict['details']['url'] = response.url
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
        if hasattr(response, 'selector'):
            selector = response.selector
        else:
            selector = response
        labels = set()
        for label, search in self.labels.items():
            found = selector.re_first(search)
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
            ingredients = str(ingredientString)
            ingredients = re.sub(self.beforeColonRegEx, ' ', ingredients)
            ingredients = re.sub(self.footnoteRegEx, ' ', ingredients)
            ingredients = re.sub(self.zutatenRegEx, ' ', ingredients)
            ingredients = ingredients.replace('*', ' ')
            ingredients = ingredients.replace('°', ' ')
            ingredients = re.sub(self.whiteSpaceRegEx, ' ', ingredients)
            ingredients = re.sub(self.decimalSepRegEx, '.', ingredients)
            ingredients = re.sub(self.htmlTagRegEx,'', ingredients) # get rid of html tags
                                                    # only works if not broken!
            ingredients = html.unescape(ingredients)
            ingredients = re.sub(self.kannSpurenRegEx, '', ingredients)
            ingredients = re.sub(self.delNoneDecDotsRegEx, '', ingredients)
            ingredients = re.split(self.splitIngredientsRegEx, ingredients)
            ingredients = [element.strip() for element in ingredients]
            ingredientList = list()
            for ingredient in ingredients:
                if ingredient not in ingredientList: # make them unique
                    ingredientList.append(ingredient)
            # ingredients = list(set(ingredients)) # make them unique /changes order
            ingredients = list(filter(None, ingredientList)) # delete empty items
            return ingredients

    def closed(self, message):
        directory = self.listOutputDirectory + os.sep
        thisTime = time.strftime('%d-%m-%Y_%H-%M')
        brandsFileName = directory + '_'.join([self.name, 'brands', thisTime]) + '.txt'
        ressourcesFileName = directory + '_'.join([self.name, 'ressources', thisTime]) + '.txt'
        labelsFileName = directory + '_'.join([self.name, 'labels', thisTime]) + '.txt'

        with codecs.open(brandsFileName, mode='w',encoding='utf-8', errors='namereplace') as file:
            file.write('\n'.join(self.brandsOUTPUT))
        with codecs.open(ressourcesFileName, mode='w', encoding='utf-8', errors='namereplace') as file:
            file.write('\n'.join(self.ressourcesOUTPUT))
        with codecs.open(labelsFileName, mode='w', encoding='utf-8', errors='namereplace') as file:
            file.write('\n'.join(self.labelsOUTPUT))