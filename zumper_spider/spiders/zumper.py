# -*- coding: utf-8 -*-
from scrapy import Spider
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from zumper_spider.items import ZumperSpiderItem
from scrapy.selector import Selector
from scrapy.http import Request
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException
import time
import json
from datetime import datetime
import re



states = {'alabama': 'al', 'alaska': 'ak', 'arizona': 'az', 'arkansas': 'ar', 'california': 'ca', 'colorado': 'co', 
        'connecticut': 'ct', 'delaware': 'de', 'district': 'dc', 'florida': 'fl', 'georgia': 'ga', 'hawaii': 'hi', 'idaho': 'id', 
        'illinois': 'il', 'indiana': 'in', 'iowa': 'ia', 'kansas': 'ks', 'kentucky': 'ky', 'louisiana': 'la', 'maine': 'me', 
        'maryland': 'md', 'massachusetts': 'ma', 'michigan': 'mi', 'minnesota': 'mn', 'mississippi': 'ms', 'missouri': 'mo', 
        'montana': 'mt', 'nebraska': 'ne', 'nevada': 'nv', 'new hampshire': 'nh', 'new jersey': 'nj', 'new mexico': 'nm',
        'new york': 'ny', 'north carolina': 'nc', 'north dakota': 'nd', 'ohio': 'oh', 'oklahoma': 'ok', 'oregon': 'or',
        'pennsylvania': 'pa', 'rhode island': 'ri', 'south carolina': 'sc', 'south dakota': 'sd', 'tennessee': 'tn',
        'texas': 'tx', 'utah': 'ut', 'vermont': 'vt', 'virginia': 'va', 'washington': 'wa', 'west virginia': 'wv',
        'wisconsin': 'wi', 'wyoming': 'wy'}

test_case = ['wy', 'wv']


class ZumperSpider(Spider):
    name = 'zumper'
    allowed_domains = ['zumper.com']
    start_urls = ['https://www.zumper.com']

    def parse(self, response):
        site = 'https://www.zumper.com/country/'
        for state in states.values():
            state_url = site + state
            # access state
            yield Request(state_url, callback=self.parse_state)


    def parse_state(self, response):
        paginators = response.xpath('//a[@class="Paginator_link__x0s5w"]/@href').extract()
        num_pages = len(paginators)

        if num_pages == 0:
            sitemap = response.xpath('//body/div/div[2]/div/div[1]/div[2]/div/a/@href').extract()
            for href in sitemap:
                district_url = self.start_urls[0] + href
                yield Request(district_url, callback=self.parse_city)
        else:
            for i in range(num_pages):
                url = response.url + '-' + str(i+1)
                yield Request(url, callback=self.parse_page)


    def parse_page(self, response):
        sitemap = response.xpath('//body/div/div[2]/div/div[1]/div[2]/div/a/@href').extract()
        for href in sitemap:
            district_url = self.start_urls[0] + href
            yield Request(district_url, callback=self.parse_city)


    def parse_city(self, response):
        href = response.xpath('//body/div/div[2]/div/div[1]/div[2]/div[7]/a/@href').extract_first()
        url = self.start_urls[0] + href
        yield Request(url, callback=self.parse_cityapt)


    def parse_cityapt(self, response):
        total_listings = response.xpath('//div[@class="MatchingCount_matchingCount__1AgB0"]/text()').extract()
        if total_listings and total_listings != []:
            total = int(re.findall(r"\d+\.?\d*", total_listings[0])[0])
            if total <= 20:
                url = response.url + '?page=1'
                yield Request(url, callback=self.parse_apt)
            else:
                numpages = total // 20 + 1
                for i in range(numpages):
                    url = response.url + '?page=' + str(i+1)
                    yield Request(url, callback=self.parse_apt)
        else:
            url = response.url + '?page=1'
            yield Request(url, callback=self.parse_apt)


    def parse_apt(self, response):
        apts = response.xpath('//div[@class="ListItem_ListItem__2erlV"]/script/text()').extract()
        for item in apts:
            script_content = json.loads(item)
            final_url = script_content['url']
            item = ZumperSpiderItem()
            item['website'] = 'www.zumper.com'
            item['home_url'] = str(script_content['url'])
            item['property_type'] = str(script_content['@type'])
            item['record_type'] = 'rent'
            item['parser_type'] = None
            item['latitude'] = script_content['geo']['latitude']
            item['longitude'] = script_content['geo']['longitude']
            item['streetaddr'] = str(script_content['address']['streetAddress'])
            item['city'] = str(script_content['address']['addressLocality'])
            item['state'] = str(script_content['address']['addressRegion'])
            item['zipcode'] = int(script_content['address']['postalCode'])
            item['country'] = 'Untied States'

            item['floor_plan'] = 'N/A'
            item['floorType'] = None
            item['lotsize'] = None
            item['stories'] = None
            item['style'] = None
            item['numofparking'] = None
            item['stainlessApplication'] = None
            item['kitchenCountertop'] = None
            item['renovation'] = None
            item['elevation'] = None
            item['elevationType'] = None
            item['datelisted'] = None
            item['inactive'] = None
            item['saleprice'] = -1
            item['yearbuilt'] = -1
            item['crawl_time'] = str(datetime.now())
            yield Request(final_url, meta={'item': item}, callback=self.parse_info)


    def parse_info(self, response):
        item = response.meta["item"]

        # numbed, num_bath_full, num_bath_part, size
        beds = response.xpath('//div[@class="GroupSummary_topInfo__fq5ON"]/div[1]/text()').extract()
        item['numbed'] = 1
        item['num_bath_full'] = -1
        item['num_bath_part'] = -1
        item['size'] = -1
        if beds and beds != []:
            temp = re.findall(r"\d+\.?\d*", beds[-1])
            if temp and temp != []:
                item['numbed'] = int(temp[0])

            bath = response.xpath('//div[@class="DesktopFloorplan_bathroomText__2PZpS"]/span/text()').extract()
            bath = re.findall(r"\d+\.?\d*", bath[-1])
            if bath and bath != []:
                item['num_bath_full'] = int(bath[0])

            sqft = response.xpath('//div[@class="DesktopFloorplan_sqftText__1_tT_"]/span/text()').extract()
            sqft = re.findall(r"\d+\.?\d*", sqft[-1])
            if sqft and sqft != []:
                item['size'] = int(sqft[0])
        else:
            detail = response.xpath('//div[@class="SummaryIcon_summaryText__2Su6m"]/text()').extract()
            bed = re.findall(r"\d+\.?\d*", detail[0])
            item['numbed'] = int(bed[0])

            bath = re.findall(r"\d+\.?\d*", detail[1])
            if len(bath) == 1:
                item['num_bath_full'] = int(bath[0])
            elif len(bath) == 2:
                item['num_bath_full'] = int(bath[0])
                item['num_bath_part'] = int(bath[1])

            sqft = re.findall(r"\d+\.?\d*", detail[2])
            if sqft and sqft != []:
                item['size'] = int(sqft[0])

        # rentalprice_min, rentalprice_max
        item['rentalprice_min'] = -1
        item['rentalprice_max'] = -1
        price = response.xpath('//div[@class="MessageSummary_priceText__3Sxbr"]/div/text()').extract()
        price = "".join(price)
        price = re.findall(r"\d+\.?\d*", price.replace(",", ""))
        if len(price) == 2:
            item["rentalprice_min"] = int(price[0])
            item["rentalprice_max"] = int(price[1])
        elif len(price) == 1:
            item["rentalprice_min"] = int(price[0])

        # description, listedBy
        desc = response.xpath('//div[@class="Description_description__1gLHl"]/div[1]/text()').extract()
        if desc and desc != []:
            item['description'] = desc[0].encode('ascii','replace')
        else:
            item['description'] = None

        listed = response.xpath('//div[@class="Description_description__1gLHl"]//a/text()').extract()
        if listed and listed != []:
            item['listedBy'] = str(listed[0])
        else:
            item['listedBy'] = None

        # Garage Parking, Swimming Pool, Fireplace, Secured Entry
        item['garage'] = -1
        item['pool'] = -1
        item['gateCommunity'] = -1
        item['fireplace'] = -1
        amentities = set(response.xpath('//div[@class="Amenity_amenity__3LSDQ"]//text()').extract())
        if 'Garage Parking' in amentities:
            item['garage'] = 1
        if 'Swimming Pool' in amentities:
            item['pool'] = 1
        if 'Secured Entry' in amentities:
            item['gateCommunity'] = 1
        if 'Fireplace' in amentities:
            item['fireplace'] = 1

        yield item
"""

# -*- coding: utf-8 -*-
from scrapy import Spider
from selenium import webdriver
from zumper_test.items import ZumperSpiderItem
from scrapy.selector import Selector
from scrapy.http import Request
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException
import time
import json
from datetime import datetime
import re


states = {'alabama': 'al', 'alaska': 'ak', 'arizona': 'az', 'arkansas': 'ar', 'california': 'ca', 'colorado': 'co', 
        'connecticut': 'ct', 'delaware': 'de', 'district': 'dc', 'florida': 'fl', 'georgia': 'ga', 'hawaii': 'hi', 'idaho': 'id', 
        'illinois': 'il', 'indiana': 'in', 'iowa': 'ia', 'kansas': 'ks', 'kentucky': 'ky', 'louisiana': 'la', 'maine': 'me', 
        'maryland': 'md', 'massachusetts': 'ma', 'michigan': 'mi', 'minnesota': 'mn', 'mississippi': 'ms', 'missouri': 'mo', 
        'montana': 'mt', 'nebraska': 'ne', 'nevada': 'nv', 'new hampshire': 'nh', 'new jersey': 'nj', 'new mexico': 'nm',
        'new york': 'ny', 'north carolina': 'nc', 'north dakota': 'nd', 'ohio': 'oh', 'oklahoma': 'ok', 'oregon': 'or',
        'pennsylvania': 'pa', 'rhode island': 'ri', 'south carolina': 'sc', 'south dakota': 'sd', 'tennessee': 'tn',
        'texas': 'tx', 'utah': 'ut', 'vermont': 'vt', 'virginia': 'va', 'washington': 'wa', 'west virginia': 'wv',
        'wisconsin': 'wi', 'wyoming': 'wy'}

states_short_1 = ['al', 'ak', 'az', 'ar', 'ca']
states_short_2 = ['co', 'ct', 'de', 'dc', 'fl']
states_short_3 = ['ga', 'hi', 'id', 'il', 'in']
states_short_4 = ['ia', 'ks', 'ky', 'la', 'me']
states_short_5 = ['md', 'ma', 'mi', 'mn', 'ms']
states_short_6 = ['mo', 'mt', 'ne', 'nv', 'nh']
states_short_7 = ['nj', 'nm', 'ny', 'nc', 'nd']
states_short_8 = ['oh', 'ok', 'or', 'pa', 'ri']
states_short_9 = ['sc', 'sd', 'tn', 'tx', 'ut']
states_short_10 = ['vt', 'va', 'wa', 'wv', 'wi', 'wy']

test_case = ['cheyenne-wy', 'rock-springs-wy', 'laramie-wy', 'cody-wy', 'casper-wy', 'mills-wy']

class Zumper1Spider(Spider):
    name = 'zumper_1'
    allowed_domains = ['zumper.com']
    start_urls = ['https://www.zumper.com']

    def parse(self, response):
        state = 'wy'
        site = 'https://www.zumper.com/country/'
        state_url = site + state
        # access the sitemap page for the state
        yield Request(state_url, callback=self.pares_1)

    def pares_1(self, response):
        paginators = response.xpath('//a[@class="Paginator_link__x0s5w"]/@href').extract()
        num_pages = len(paginators)

        if num_pages == 0:
            url = 'https://www.zumper.com'
            sitemap = response.xpath('//body/div/div[2]/div/div[1]/div[2]/div/a/@href').extract()
            for href in sitemap:
                district_url = url + href
                yield Request(district_url, callback=self.parse_2)
        else:
            for i in range(num_pages):
                url = response.url + '-' + str(i+1)
                yield Request(url, callback=self.parse_page)

    def parse_page(self, response):
        url = 'https://www.zumper.com'
        sitemap = response.xpath('//body/div/div[2]/div/div[1]/div[2]/div/a/@href').extract()
        for href in sitemap:
            district_url = url + href
            yield Request(district_url, callback=self.parse_2)

    def parse_2(self, response):
        url = 'https://www.zumper.com'
        href = response.xpath('//body/div/div[2]/div/div[1]/div[2]/div[7]/a/@href').extract_first()
        apt = url + href

        driver = webdriver.Chrome('/Users/chuanqinqiu/Downloads/chromedriver')
        driver.get(apt)
        time.sleep(0.5)
        sel = Selector(text=driver.page_source)
        while True:
            try:
                load_more = driver.find_element_by_xpath('//button[text()="Load more listings"]')
                time.sleep(0.7)
                load_more.click()
            except:
                break

        sel2 = Selector(text=driver.page_source)
        driver.close()
        for apt in sel2.xpath('//div[@class="ListItem_ListItem__2erlV"]/script/text()').extract():
            script_content = json.loads(apt)
            final_url = script_content['url']
            item = ZumperSpiderItem()
            item['website'] = 'www.zumper.com'
            item['record_type'] = 'rent'
            item['parser_type'] = None
            item['country'] = 'Untied States'
            item['home_url'] = str(script_content['url'])
            item['property_type'] = str(script_content['@type'])
            item['latitude'] = script_content['geo']['latitude']
            item['longitude'] = script_content['geo']['longitude']
            item['streetaddr'] = str(script_content['address']['streetAddress'])
            item['city'] = str(script_content['address']['addressLocality'])
            item['states'] = str(script_content['address']['addressRegion'])
            item['zipcode'] = int(script_content['address']['postalCode'])
            item['crawl_time'] = str(datetime.now())
            yield Request(final_url, meta={'item': item}, callback=self.parse_3)


    def parse_3(self, response):
        item = response.meta["item"]
        
        price = response.xpath('//div[@class="MessageSummary_priceText__3Sxbr"]/div/text()').extract()
        price = "".join(price)
        price = re.findall(r"\d+\.?\d*", price.replace(",", ""))
        item['rentalprice_min'] = -1
        item['rentalprice_max'] = -1
        if len(price) == 2:
            item["rentalprice_min"] = int(price[0])
            item["rentalprice_max"] = int(price[1])
        elif len(price) == 1:
            item["rentalprice_min"] = int(price[0])

        beds = response.xpath('//div[@class="GroupSummary_topInfo__fq5ON"]/div[1]/text()').extract()
        if beds and beds != []:
            item['numbed'] = 1
            item['num_bath_full'] = -1
            item['num_bath_part'] = -1
            item['size'] = -1
            temp = re.findall(r"\d+\.?\d*", beds[-1])
            if temp and temp != []:
                item['numbed'] = int(temp[0])
            
            bath = response.xpath('//div[@class="DesktopFloorplan_bathroomText__2PZpS"]/span/text()').extract()
            bath = re.findall(r"\d+\.?\d*", bath[-1])
            if bath and bath != []:
                item['num_bath_full'] = int(bath[0])

            sqft = response.xpath('//div[@class="DesktopFloorplan_sqftText__1_tT_"]/span/text()').extract()
            sqft = re.findall(r"\d+\.?\d*", sqft[-1])
            if sqft and sqft != []:
                item['size'] = int(sqft[0])

        else:
            detail = response.xpath('//div[@class="SummaryIcon_summaryText__2Su6m"]/text()').extract()
            item['numbed'] = 1
            item['num_bath_full'] = -1
            item['num_bath_part'] = -1
            item['size'] = -1

            bed = re.findall(r"\d+\.?\d*", detail[0])
            item['numbed'] = int(bed[0])
            bath = re.findall(r"\d+\.?\d*", detail[1])
            if len(bath) == 1:
                item['num_bath_full'] = int(bath[0])
            elif len(bath) == 2:
                item['num_bath_full'] = int(bath[0])
                item['num_bath_part'] = int(bath[1])

            sqft = re.findall(r"\d+\.?\d*", detail[2])
            if sqft and sqft != []:
                item['size'] = int(sqft[0])


        yield item


"""