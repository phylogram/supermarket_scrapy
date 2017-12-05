# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import re
import scrapy
from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from selenium import webdriver

class SupermarketScrapySpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SkipNonProductsMeinDM(): 
    'filters products for DM'
    categoryURL = 'https://www.meindm.at/ernaehrung/'
    def process_request(self, request, spider):
        if spider.name == 'MeinDMatShop':
            sitemap = 'sitemap' in request.url
            category = self.categoryURL in request.url
            robot = 'robots.txt' in request.url
            if not(sitemap or category or robot):
                raise IgnoreRequest
        return None
    

class UseChrome():
    '''
    get requests from scrapy, uses selenium webdriver and send responses back.
    Does not pass them to scrapy downloaders. Set Spiders Names in self.spiderNames
    '''    
    spiderNames = ['MerkurShop', 'BillaShop']
    def __init__(self):
        options = webdriver.ChromeOptions()
        #options.binary_location = '/usr/bin/chromium'
        #options.add_argument('headless') I don't know why - headless is extremly slow with my computer
        options.add_argument('disable-gpu')
        options.add_argument('window-size=1200x600')
        self.browser = webdriver.Chrome(chrome_options=options)

        self.browser.implicitly_wait(2)
        
    def process_request(self, request, spider):
        if spider.name not in self.spiderNames:
            return None
        elif 'sitemap' in request.url:
            return None
        elif 'robots.txt' in request.url:
            return None
        else:
            self.browser.get(request.url)
            response = scrapy.http.HtmlResponse(self.browser.current_url,
                                            body=self.browser.page_source,
                                            encoding='utf-8',
                                            request=request)
            return response
        

class UseChromePostalCodes():
    '''
    Passes Requests to different selenium Chrome rowsers, with distinct cookies.
    Each postal code (plz) gets an own browser.
    Slectors / Click behavior is distinct for each spider by name.
    See self. process_request
    '''
    browsers = {} # {plz: browser}
    def getNewBrowser(self):
        options = webdriver.ChromeOptions()
        #options.binary_location = '/usr/bin/chromium'
        #options.add_argument('headless') doesn't work with headless ? bug?
        options.add_argument('disable-gpu')
        options.add_argument('window-size=1200x600')
        browser = webdriver.Chrome(chrome_options=options)
        browser.implicitly_wait(2)
        return browser
    def process_request(self, request, spider):
        if 'plz' not in request.meta:
            return None
        plz = request.meta['plz']
        if plz in self.browsers:
            browser = self.browsers[plz]
            browser.get(request.url)
            # scroll down the page to get ajax loads
            browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        else:
            browser = self.getNewBrowser()
            self.browsers[plz] = browser
            browser.get(request.url)
            if spider.name == 'AllYouNeedIsFresh':
                form = browser.find_element_by_id('zipCodeForm:zipCode')
                button = browser.find_element_by_id("zipCodeForm:submit")
                form.send_keys(plz)
                button.click()
            if spider.name == 'ReweShop':
                form = browser.find_element_by_id('marketchooser-search-value')
                form.send_keys(plz)
                button = browser.find_element_by_id('location-search-trigger')
                button.click()
                # Here you can choose between delivery and pickup. For pickup you have to
                # choose a store. There are many
                divButton = browser.find_element_by_css_selector('div .delivery-service-action')
                divButton.click()
                #Say ok/go
                goButton = browser.find_element_by_id('mc-success-trigger')
                goButton.click()
            
        response = scrapy.http.HtmlResponse(browser.current_url,
                                            body=browser.page_source,
                                            encoding='utf-8',
                                            request=request)
        return response
    def __del__(self): ### Right place to do this? To Do // Check!
       for browser in self.browsers.values():
           browser.quit()
       
class MyTimeShopFilter():
    'filters requests'
    spiderNames = ['MyTimeShop']
    def process_request(self, request, spider):
        if spider.name not in self.spiderNames:
            return None
        elif len(request.url.split('/')) != 4:
                raise IgnoreRequest
        else:
            return None
        
class EdekaFilter():
    'filters requests'
    food = re.compile('/Lebensmittel/')
    noCategory = re.compile('https://www\.edeka24\.de/[^/]+')
    def process_request(self, request, spider):
        if spider.name != 'EdekaShop':
            return None
        isFood = re.match(self.food, request.url)
        hasNoCategory = re.match(self.noCategory, request.url)
        
        if isFood or hasNoCategory:
            return None # pass
        else:
            raise IgnoreRequest
class BillaShopFilter():
    '''We can't use stemap_rules fromscrapy
    because the billa sitemap has no meta-sitemap format'''
    baseSitemap = 'https://shop.billa.at/sitemap'
    def process_request(self, request, spider):
        if spider.name != 'BillaShop':
            return None
        if self.baseSitemap == request.url:
            return None
        if 'sitemap' in request.url:
            # all product sitemaps contain "warengruppe" (product group)
            if 'warengruppe' not in request.url:
                raise IgnoreRequest
        return None
    
    
    