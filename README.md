# Install!

    host# apt-get install --no-install-recommends vagrant ansible virtualbox

# Setup!

    host$ vagrant up --provider=virtualbox
    host$ vagrant ssh

# Scrape!

We recommended using `scrapy`. It is installed in the box.

`scrapy` is a scraping *framework*: it lets you build and run spiders.
It can also output the results into a JSON file.

By default the `scrapy` scrapers work on the source HTML it gets from the
server, not the computed HTML i.e. any JavaScript magic would not have been
applied.

You yan work around this by using `chrome` in headless mode (also installed in
the box). See the example `javascript_source` in the
`supermarket_scrapy/supermarket_scrapy/spiders/` directory.

For more resources on `scrapy` see:
https://doc.scrapy.org/en/latest/intro/tutorial.html

## Tasks

* Link discovery
* Automatically crawl the page, beginning from a start page, automatically
  finding the next page
* XPath or CSS selections of the needed page contents
* Clean the data from leading/trailing whitespace
* UTF-8 conversions
* Split the data strings into parts if necessary
* Map ingredients to resources
* Search for labels

## Hints

* Explore an URL with `scrapy shell 'https://example.com'`
* Use and share middlewares and pipelines
* Use "Copy XPath" from the browser

# Validate!

    guest$ cd hostdir
    guest$ python checkschema.py --schema-file schema.json --data-file testdata.json --brands-file brands.list --labels-file labels.list --resources-file resources.list

# Requirements

* Chrome or Chromium 59+ for headless mode
* Firefox 56+ for "Copy XPath" in context menu
* Python 3

# Example

  scrape and write JSON file:

    cd supermarket-scrapy
    scrapy crawl javascript_source -o ../data.json
    cd ..

(optional) inspect data e.g. with

    cat data.json | jq

check the schema>

    python checkschema.py --schema-file schema.json --data-file data.json --check-brands --brands-file brands.list
    echo "Ja! Natürlich" >> brands.list
    python checkschema.py --schema-file schema.json --data-file data.json --check-brands --brands-file brands.list

# URLs

* Scrapy documentation: https://doc.scrapy.org/en/latest/
* Selenium documentation: https://selenium-python.readthedocs.io/
* XPath tutorial: https://blog.scrapinghub.com/2016/10/27/an-introduction-to-xpath-with-examples/
* Headless Chrome: https://developers.google.com/web/updates/2017/04/headless-chrome
* Headless Chrome and Selenium: https://intoli.com/blog/running-selenium-with-headless-chrome/

other suggestions:

* Beautiful Soup "for pulling out data from HTML": https://www.crummy.com/software/BeautifulSoup/bs4/doc/
