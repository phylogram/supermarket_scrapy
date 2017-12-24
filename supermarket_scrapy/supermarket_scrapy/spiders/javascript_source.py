# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from selenium import webdriver


class JavascriptSourceSpider(scrapy.Spider):
    name = 'javascript_source'
    allowed_domains = ['janatuerlich.at']
    start_urls = [
        'http://www.janatuerlich.at/Sonderkapitel/Produkte/Produkte/Portal.aspx?produktgruppe=5101&produkt=200',
        'http://www.janatuerlich.at/Sonderkapitel/Produkte/Produkte/Portal.aspx?produktgruppe=5102&produkt=8632'
    ]

    def __init__(self, *args, **kwargs):
        super(JavascriptSourceSpider, self).__init__(*args, **kwargs)
        self.download_delay = 0.25

        # instantiate Chrome headless
        options = webdriver.ChromeOptions()
        options.binary_location = '/usr/bin/chromium'
        options.add_argument('headless')
        options.add_argument('disable-gpu')
        options.add_argument('window-size=1200x600')
        self.browser = webdriver.Chrome(chrome_options=options)

        self.browser.implicitly_wait(60)

    def parse(self, response):
        # fetch page and create form for scrapy to handle (Selector)
        self.browser.get(response.url)
        source = self.browser.page_source
        sel = Selector(text=source)

        # address the desired element
        name = sel.xpath('/html/body/form/div[13]/div[2]/div[1]/div/div[1]/div[2]/div[2]/h1/text()').extract_first()
        ingredients = sel.xpath('/html/body/form/div[13]/div[2]/div[1]/div/div[1]/div[4]/div[2]/ul/li/text()').extract()
        image_src = sel.xpath('/html/body/form/div[13]/div[2]/div[1]/div/div[1]/div[2]/div[1]/img/@src').extract_first()

        # emit the result for scrapy to output
        yield {
            'name': name,
            'brand': "Ja! Natürlich",
            'ingredients': ingredients,
            'labels': ["Ja Natürlich"],
            'stores': ["Billa", "Merkur"],
            'details': {
                'image_url': image_src
            }
        }
