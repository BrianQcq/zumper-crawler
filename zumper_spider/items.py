# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZumperSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    website = scrapy.Field()
    record_type = scrapy.Field()
    parser_type = scrapy.Field()
    country = scrapy.Field()
    lotsize = scrapy.Field() ###!!!###
    stories = scrapy.Field() ###!!!###
    style = scrapy.Field() ###!!!###
    numofparking = scrapy.Field() ###!!!###
    stainlessApplication = scrapy.Field() ###!!!###
    floorType = scrapy.Field() ###!!!###
    kitchenCountertop = scrapy.Field() ###!!!###
    renovation = scrapy.Field() ###!!!###
    elevation = scrapy.Field() ###!!!###
    elevationType = scrapy.Field() ###!!!###
    datelisted = scrapy.Field() ###!!!###
    inactive = scrapy.Field() ###!!!###

    home_url = scrapy.Field()
    property_type = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    streetaddr = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    zipcode = scrapy.Field()

    size = scrapy.Field() ###!!!###
    garage = scrapy.Field() ###!!!###
    pool = scrapy.Field() ###!!!###
    gateCommunity = scrapy.Field() ###!!!###
    fireplace = scrapy.Field() ###!!!###
    description = scrapy.Field() ###!!!###
    crawl_time = scrapy.Field()

    rentalprice_min = scrapy.Field()
    rentalprice_max = scrapy.Field()
    saleprice = scrapy.Field()
    numbed = scrapy.Field()
    num_bath_full = scrapy.Field()
    num_bath_part = scrapy.Field()

    floor_plan = scrapy.Field()
    listedBy = scrapy.Field()
    yearbuilt = scrapy.Field()
"""

#- website: www.zumper.com
#- home_url: script['url']
#- property_type: script['@type']
#- record_type: rent
#- parser_type: NULL
#- latitude: script['geo']['latitude']
#- longitude: script['geo']['longitude']
#- streetaddr: script['address']['streetAddress']
#- city: script['address']['addressLocality']
#- states: script['address']['addressRegion']
#- zipcode: script['address']['postalCode']
#- country: United States
#- numbed: 
#- num_bath_full: 
#- num_bath_part: 
#- rentalprice_min: 
#- rentalprice_max: 
#- saleprice: 
#- floor_plan: 
#- lotsize: NULL
#- stories: NULL
#- size: page detail sqft
#- style: NULL
#- numofparking: NULL
#- stainlessApplication: NULL
#- floorType: NULL
#- kitchenCountertop: NULL
#- renovation: NULL
#- elevation: NULL
#- elevationType: NULL
#- crawl_time: 
#- datelisted: NULL
#- inactive: NULL
#- description: page description section
#- listedBy: 

- yearbuilt:
#- garage: page building section (0 or 1) # Garage Parking
#- pool: page building section (0 or 1) # Swimming Pool
#- gateCommunity: page building section (0 or 1) # Secured Entry
#- fireplace: page unit section (0 or 1) # Fireplace

"""