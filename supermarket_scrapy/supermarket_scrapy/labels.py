# -*- coding: utf-8 -*-
"""
Created on Sat Dec  2 11:17:52 2017

@author: Philip Röggla
Retrieves labels from supplychainge and compiles regexes for searching websites
"""
import json
import re
import requests

labels = dict()

jsonString = requests.get("https://api.supplychainge.org/api/v1/labels").text
labelsJSON = json.loads(jsonString)

for item in labelsJSON['items']:
    # make sure we don't care for Capitalisation & duplication
    values = {value: value.lower() for value in item['name'].values()}
    for label, search in values.items():
       labels[label] = re.compile('\W(' + search + ')\W', flags=re.IGNORECASE)
