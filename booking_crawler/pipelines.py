# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

from .items import BookingHotel, TripAdvisorRestaurant


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'booking')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        # self.db[self.collection_name_articles].delete_many({})

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, BookingHotel) or isinstance(item, TripAdvisorRestaurant):
            # self.db[self.collection_name_articles].insert_one(dict(article))
            if isinstance(item, BookingHotel):
                collection_name = "hotel"
                database_name = "booking"

            elif isinstance(item, TripAdvisorRestaurant):
                collection_name = "restaurant"
                database_name = "tripadvisor"

            self.client[database_name][collection_name].update({"_id": dict(item)["_id"]},
                                                          dict(item),
                                                          upsert=True)
        return item
