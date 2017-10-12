import click
import json
import jsonschema


def _read_as_list(file_path):
    """return lines as list

    filter comments (starting with '#') and empty strings
    """
    lines = []

    with open(file_path, 'r') as stream:
        lines = [line.strip() for line in stream if not line.startswith('#')]

    return list(filter(None, lines))


@click.command()
@click.option('--schema-file', type=click.Path(exists=True), required=True)
@click.option('--data-file', type=click.Path(exists=True), required=True)
@click.option('--check-brands/--no-check-brands', default=True)
@click.option('--brands-file', type=click.Path(exists=True), default=None)
@click.option('--check-labels/--no-check-labels', default=True)
@click.option('--labels-file', type=click.Path(exists=True), default=None)
def validate(schema_file, data_file, check_brands, brands_file, check_labels, labels_file):
    schema = {}
    with open(schema_file, 'r') as stream:
        schema = json.load(stream)

    data = {}
    with open(data_file, 'r') as stream:
        data = json.load(stream)

    if not check_brands:
        print(click.style("Not checking brands...", fg='yellow'))
    else:
        print(click.style("Checking brands...", fg='green'))
        if brands_file:
            brands = _read_as_list(brands_file)
        else:
            brands = []

        schema['items']['properties']['brand']['enum'] = brands
        print("Brands: {}".format(brands))

    if not check_labels:
        print(click.style("Not checking labels...", fg='yellow'))
    else:
        print(click.style("Checking labels...", fg='green'))
        if labels_file:
            labels = _read_as_list(labels_file)
        else:
            labels = []

        schema['items']['properties']['labels']['items']['enum'] = labels
        print("Labels: {}".format(labels))

    # Validate!
    jsonschema.validate(data, schema)


if __name__ == '__main__':
    validate()
