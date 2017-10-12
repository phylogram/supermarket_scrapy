import click
import json
import jsonschema


@click.command()
def validate():
    schema = {}
    with open('schema.json', 'r') as stream:
        schema = json.load(stream)

    data = {}
    with open('testdata.json', 'r') as stream:
        data = json.load(stream)

    jsonschema.validate(data, schema)


if __name__ == '__main__':
    validate()
