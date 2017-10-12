# Installation

    host# apt-get install --no-install-recommends vagrant ansible virtualbox

# Setup

    host$ vagrant up --provider=virtualbox
    host$ vagrant ssh

# Validate

    guest$ cd hostdir
    guest$ python checkschema.py --schema-file schema.json --data-file testdata.json --brands-file brands.list --labels-file labels.list --resources-file resources.list
