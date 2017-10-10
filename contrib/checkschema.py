import json
import jsonschema

schema = {}
with open('schema.json', 'r') as stream:
    schema = json.load(stream)

data = {}
with open('testdata.json', 'r') as stream:
    data = json.load(stream)

jsonschema.validate(data, schema)
