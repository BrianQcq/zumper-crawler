# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

class ZumperSpiderPipeline(object):
	def __init__(self, db):
		self.db = db

	@classmethod
	def from_settings(cls, settings):
		dbparams=dict(
			host=settings['MYSQL_HOST'],
			db=settings['MYSQL_DBNAME'],
			user=settings['MYSQL_USER'],
			passwd=settings['MYSQL_PASSWD'],
		)
		db = pymysql.connect(dbparams['host'], dbparams['user'], dbparams['passwd'], dbparams['db'])
		return cls(db)

    def process_item(self, item, spider):
    	cursor = self.db.cursor()
    	result = None
    	sql = "INSERT INTO `zumper_2019` (website, home_url, property_type, record_type, parser_type, latitude, longitude, streetaddr, city, state, zipcode, country, numbed, num_bath_full, num_bath_part, rentalprice_min, rentalprice_max, saleprice, yearbuilt, floor_plan, garage, lotsize, stories, size, pool, style, numofparking, gatedCommunity, stainlessAppliances, fireplace, floorType, kitchenCountertop, renovation, elevation, elevationType, description, crawl_time, datelisted, inactive, listedBy) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    	try:
    		result = cursor.execute(sql, (item['website'], item['home_url'], item['property_type'], item['record_type'], item['parser_type'], item['latitude'], item['longitude'], item['streetaddr'], item['city'], item['state'], item['zipcode'], item['country'], item['numbed'], item['num_bath_full'], item['num_bath_part'], item['rentalprice_min'], item['rentalprice_max'], item['saleprice'], item['yearbuilt'], item['floor_plan'], item['garage'], item['lotsize'], item['stories'], item['size'], item['pool'], item['style'], item['numofparking'], item['gateCommunity'], item['stainlessApplication'], item['fireplace'], item['floorType'], item['kitchenCountertop'], item['renovation'], item['elevation'], item['elevationType'], item['description'], item['crawl_time'], item['datelisted'], item['inactive'], item['listedBy']))
    		self.db.commit()
    	except Exception:
    		traceback.print_exc()
    		self.db.rollback()
        return item

    def spider_closed(self, spider):
    	self.db.close()