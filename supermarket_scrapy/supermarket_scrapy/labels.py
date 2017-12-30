# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 11:17:52 2017

@author: Philip Röggla
Retrieves labels from supplychainge and
and compiles regexes for searching websites
"""
import json
import re
import requests

from scrapy.http import HtmlResponse
import supermarket_scrapy.cleanString as cleanString

scURL = 'https://api.supplychainge.org/api/v1/labels'
elURL = 'http://www.ecolabelindex.com/ecolabels/?st=category,food'

values = set('bio') # add here labels you want to include manually. Don't forget: lowercase
""" A set of labels {fullname lower}"""
labels = dict()
""" A dict of RegExes for any thinkable context - see below {lowercase_fullname: regex}"""

# To slow: regExTemplate = '((?<![a-z0-9]){lowercase}(?![a-z0-9])|(?<![A-Z0-9]){cap}(?![a-z0-9])|(?<![A-Z0-9]){allCap}(?![A-Z0-9]))'
# """ See Test below (commentary) """
regExTemplate = '[\W\n]{{1}}{label}[\W\n]{{1}}'
openingParRegEx = re.compile('\s*\(.*')
""" finds opening Parantheses and deletes them and everything beyond"""
# get our labels from supplychainge
jsonString = requests.get(scURL).text
labelsJSON = json.loads(jsonString)

for item in labelsJSON['items']:
    row = {value.lower() for value in item['name'].values()}
    values = values.union(row)

# get more labels from http://www.ecolabelindex.com/ecolabels
r = requests.get(elURL)
response = HtmlResponse(elURL, body=r.text, encoding='utf-8')
labelDescField = response.xpath('//td/h4[@class="cuddle"]/a')   
for value in labelDescField.extract():
    value = value.lower()
    value = cleanString.cleanString(value)
    # get rid of broken parentheses
    if '(' in value and not ')' in value:
        value = re.sub(openingParRegEx, '', value)
    elif ')' in value and not '(' in value:
        value = None
    if not value:
        continue
    values.add(value)
    
# Make RegExes!
for value in values:
    if len(value) < 3:
        continue
    
    # The following is too slow
    # lower = value
    # cap = value.capitalize() #SLOW
    # Now: 'One two three' -> 'One [Tt]wo [Tt]hree' to catch more
    #capList = []
    #for word in cap.split(' '):
        # Find the first letter
     #   first = None
      #  for letter in range(len(word)-1, -1, -1):
       #     first = letter if word[letter].isalpha() else None
        #if first is not None and word[first].islower():
         #   capAmb = '[' + word[first].upper() + word[first] + ']'
          #  word = word[:first] + capAmb + word[first+1:]
        #capList.append(word)
    #cap = ' '.join(capList)
    #allCap = value.upper()
    #regExString = regExTemplate.format(lowercase=lower, cap=cap, allCap=allCap)
    regExString = regExTemplate.format(label=value,  flags=re.IGNORECASE)
    regEx = re.compile(regExString)
    labels[value] = regEx


# In: testString = '\nfairtrade\n\nfairtrade\nfairtrade>\nfairtradeA\nfairtradea\nfairtrade666\nfairtrade \nFairtrade\n\nFairtrade\nFairtrade>\nFairtradeA\nFairtradea\nFairtrade666\nFairtrade \nFAIRTRADE\n\nFAIRTRADE\nFAIRTRADE>\nFAIRTRADEA\nFAIRTRADEa\nFAIRTRADE666\nFAIRTRADE fairtrade\nfairtradefairtrade>fairtradeAfairtradeafairtrade666fairtrade Fairtrade\nFairtradeFairtrade>FairtradeAFairtradeaFairtrade666Fairtrade FAIRTRADE\nFAIRTRADEFAIRTRADE>FAIRTRADEAFAIRTRADEaFAIRTRADE666FAIRTRADE >fairtrade\n>fairtrade>fairtrade>>fairtradeA>fairtradea>fairtrade666>fairtrade >Fairtrade\n>Fairtrade>Fairtrade>>FairtradeA>Fairtradea>Fairtrade666>Fairtrade >FAIRTRADE\n>FAIRTRADE>FAIRTRADE>>FAIRTRADEA>FAIRTRADEa>FAIRTRADE666>FAIRTRADE Afairtrade\nAfairtradeAfairtrade>AfairtradeAAfairtradeaAfairtrade666Afairtrade AFairtrade\nAFairtradeAFairtrade>AFairtradeAAFairtradeaAFairtrade666AFairtrade AFAIRTRADE\nAFAIRTRADEAFAIRTRADE>AFAIRTRADEAAFAIRTRADEaAFAIRTRADE666AFAIRTRADE afairtrade\nafairtradeafairtrade>afairtradeAafairtradeaafairtrade666afairtrade aFairtrade\naFairtradeaFairtrade>aFairtradeAaFairtradeaaFairtrade666aFairtrade aFAIRTRADE\naFAIRTRADEaFAIRTRADE>aFAIRTRADEAaFAIRTRADEaaFAIRTRADE666aFAIRTRADE 666fairtrade\n666fairtrade666fairtrade>666fairtradeA666fairtradea666fairtrade666666fairtrade 666Fairtrade\n666Fairtrade666Fairtrade>666FairtradeA666Fairtradea666Fairtrade666666Fairtrade 666FAIRTRADE\n666FAIRTRADE666FAIRTRADE>666FAIRTRADEA666FAIRTRADEa666FAIRTRADE666666FAIRTRADE  fairtrade\n fairtrade fairtrade> fairtradeA fairtradea fairtrade666 fairtrade  Fairtrade\n Fairtrade Fairtrade> FairtradeA Fairtradea Fairtrade666 Fairtrade  FAIRTRADE\n FAIRTRADE FAIRTRADE> FAIRTRADEA FAIRTRADEa FAIRTRADE666 FAIRTRADE '
# In: name = 'fairtrade'
# In: testRegex = regExTemplate.format(lowercase=name.lower(), cap=name.capitalize(), allCap=name.upper())
# In: re.findall(testRegex, testString)
"""  Out: ['fairtrade',
 'fairtrade',
 'fairtrade',
 'fairtrade',
 'fairtrade',
 'Fairtrade',
 'Fairtrade',
 'Fairtrade',
 'Fairtrade',
 'Fairtrade',
 'FAIRTRADE',
 'FAIRTRADE',
 'FAIRTRADE',
 'FAIRTRADE',
 'FAIRTRADE',
 'fairtrade',
 'fairtrade',
 'Fairtrade',
 'Fairtrade',
 'Fairtrade',
 'Fairtrade',
 'FAIRTRADE',
 'fairtrade',
 'fairtrade',
 'fairtrade',
 'fairtrade',
 'fairtrade',
 'Fairtrade',
 'Fairtrade',
 'Fairtrade',
 'Fairtrade',
 'Fairtrade',
 'FAIRTRADE',
 'FAIRTRADE',
 'FAIRTRADE',
 'FAIRTRADE',
 'FAIRTRADE',
 'fairtrade',
 'fairtrade',
 'fairtrade',
 'fairtrade',
 'fairtrade',
 'Fairtrade',
 'Fairtrade',
 'Fairtrade',
 'Fairtrade',
 'FAIRTRADE',
 'FAIRTRADE',
 'FAIRTRADE',
 'FAIRTRADE',
 'FAIRTRADE',
 'fairtrade',
 'fairtrade',
 'fairtrade',
 'fairtrade',
 'fairtrade',
 'Fairtrade',
 'Fairtrade',
 'Fairtrade',
 'Fairtrade',
 'Fairtrade',
 'FAIRTRADE',
 'FAIRTRADE',
 'FAIRTRADE',
 'FAIRTRADE',
 'FAIRTRADE'] """
     