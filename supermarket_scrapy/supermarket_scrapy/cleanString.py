#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 28 14:23:50 2017

@author: phylogram
"""
import codecs
import html
import re
from urllib import parse

whiteSpaceRegEx = re.compile('[\s]')
htmlTagRegEx = re.compile('<\/{0,1}\w.*?>')

def cleanString(string):
    'Cleans Strings - html, utf-8 encoding ... '
    if not string:
        return None
    string = str(string)
    string = re.sub(whiteSpaceRegEx, ' ', string)
    string = html.unescape(string)
    string = re.sub(htmlTagRegEx, '', string)
    string = codecs.encode(string)
    string = codecs.decode(string, encoding='utf-8', errors='namereplace')
    string = parse.unquote(string)
    string = string.strip()
    return string       

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