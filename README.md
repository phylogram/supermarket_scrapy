# Before you start

## Abstract Shop Spider

Besides the scrapy parents Spider and SitemapSpider, allof the new spiders have the 
AbstractShopSpider as parent, where the main functionallity for the json schema is 
provided. This class is not really abstract though.

## Labels at ./supermarket_scrapy

Retrieves labels from supplychainge and compiles regexes for searching websites

## What Do you need:

Often selenium & chrome. For amazon we need to read image text with tesseract and German
language training data (https://github.com/tesseract-ocr/tesseract/wiki).

### MeinDMatShopSpider
* type = Sitemap
* name = 'MeinDMatShop'
* sitemap_urls = ['https://www.meindm.at/nl/sitemap/sitemap-shop.xml']
* allowed_domains = ['meindm.at']

* Needs: Downloader Middleware: 'supermarket_scrapy.middlewares.skipNonProductsMeinDM'

### LebensmittelShopSpider
* type = Spider
* name = 'LebensmittelShop'
* start_urls = ['https://www.lebensmittel.de/?subd=0']
* store = 'Lebensmittel.de'

### AlnaturaShopSpider
* type = Sitemap
* name = 'AlnaturaShop'
* sitemap_urls = ['https://www.alnatura-shop.de/medias/PRODUCT-de-EUR-479627737118262662.xml?context=bWFzdGVyfHJvb3R8NzI2MDI1fHRleHQveG1sfGhkOS9oZTcvOTA5NjQ3ODU4ODk1OC54bWx8N2JmNzFlOWQxM2Q3YTAwMWQ5MzFiOTk1NGQ0OTdjMGVhYWE0YTBiY2U5YmYyNDJkNzkyNTZmODhkNTlmNWMwNQ']
* store = 'Alnatura'

### KauflandShopSpider
* type = Spider
* name = 'KauflandShop'
* start_urls = ['https://shop.kaufland.de/search?sort=relevance&pageSize=48&source=search']
* allowed_domains = ['shop.kaufland.de']

### DMShopSpider
* type = Spider
* name = 'DMShop'
* store = 'dm'
* start_urls = ['https://www.dm.de/']
* allowed_domains = ['dm.de']

### EdekaShopSpider
* type = sitemap
name = 'EdekaShop'
sitemap_urls = ['https://www.edeka24.de/sitemaps/sitemap_0-products-0.xml']
store = 'Edeka'

* Needs: Downloader Middleware: 'supermarket_scrapy.middlewares.EdekaFilter'

### BillaShopSpider
* type = Sitemap
* name = 'BillaShop'
* sitemap_urls = ['https://shop.billa.at/sitemap']
* store = ['Billa']

* Needs: Downloader Middleware: 'supermarket_scrapy.middlewares.BillaShopFilter'
* Needs: Downloader Middleware: 'supermarket_scrapy.middlewares.useChrome'
* Needs: selenium Chrome

*super slow!!!!! *

chrome warning: A parser blocking cross site script [...] is invoked via document.write.
The network request MAY be blocked in the browser in this or a future load due to poor 
network connectivity. [...]

### AmazonLebensmittelShopSpider
* type = Spider
* name = 'AmazonLebensmittelShop'

This is the Food – Featured Categories node
As far as i understand it, alle food should be in this subcategory
 Which provides a list of products with pagination
start_urls = ['https://www.amazon.de/b?node=344162031']
allowed_domains = ['amazon.de']
store = ['amazon']

#### Needs!
* Needs: python: PIL.Image
    * Extern: tesseract with german language training set!
    https://github.com/tesseract-ocr/tesseract/wiki
    set tesseractDataPath and tesseractExePath in properties!

### AllYouNeedFreshShopSpider
* type = Spider
* name = 'AllYouNeedFresh'
* store = 'allyouneedfresh'
* allowed_domains = ['allyouneedfresh.de']

* Needs: Downloader Middleware: 'supermarket_scrapy.middlewares.UseChromePostalCodes'

Opens page with various postal codes. For some reason, headless Chrome or Firefox does
not work (time out). Bug?

### LidlShopSpider
* type = Sitemap
* name = 'LidlShop'
* store = ['Lidl']
* sitemap_urls = ['https://www.lidl.de/robots.txt'] # will lead to sitemap 
* sitemap_follow =  [re.compile('product', flags=re.IGNORECASE)]

### MerkurShopSpider
* type = Sitemap
* name = 'MerkurShop'
* sitemap_urls = ['https://www.merkurmarkt.at/sitemap_products.xml']
* allowed_domains = ['merkurmarkt.at']
* store = ['Merkur']

* Needs: Downloader Middleware: 'supermarket_scrapy.middlewares.useChrome'
* Needs: Selenium Chrome

### MyTimeShopSpider
* type = Sitemap
* name = 'MyTimeShop'
* sitemap_urls = ['https://www.mytime.de/sitemap.xml']
* store = ['myTime.de']

* Needs: Downloader Middleware: 'supermarket_scrapy.middlewares.MyTimeShopFilter'

### ReweShopSider
* type = Spider
* name = 'ReweShop'
* start_url = 'https://shop.rewe.de/productList'

* Needs: Downloader middleware: 'supermarket_scrapy.middlewares.UseChromePostalCodes'
* Needs: Selenium Chrome

Opens page with various postal codes.