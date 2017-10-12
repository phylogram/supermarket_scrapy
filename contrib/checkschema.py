import click
import json
import jsonschema


@click.command()
@click.option('--schema-file', type=click.Path(exists=True), required=True)
@click.option('--data-file', type=click.Path(exists=True), required=True)
def validate(schema_file, data_file):
    schema = {}
    with open(schema_file, 'r') as stream:
        schema = json.load(stream)

    data = {}
    with open(data_file, 'r') as stream:
        data = json.load(stream)

    jsonschema.validate(data, schema)


if __name__ == '__main__':
    validate()
