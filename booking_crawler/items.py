# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class BookingHotel(scrapy.Item):
    _id = scrapy.Field()
    description = scrapy.Field()
    name = scrapy.Field()
    images = scrapy.Field()
    localisation = scrapy.Field()
    address = scrapy.Field()
    rate = scrapy.Field()
    photos = scrapy.Field()
    crawled_at = scrapy.Field()
    facilities = scrapy.Field()
    reviews = scrapy.Field()
    lat = scrapy.Field()
    lon = scrapy.Field()
    url = scrapy.Field()
    country = scrapy.Field()

class TripAdvisorRestaurant(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    rate = scrapy.Field()
    photos = scrapy.Field()
    crawled_at = scrapy.Field()
    reviews = scrapy.Field()
    lat = scrapy.Field()
    lon = scrapy.Field()
    url = scrapy.Field()
    country = scrapy.Field()
    phone = scrapy.Field()
    website = scrapy.Field()
    loc_id = scrapy.Field()
    city = scrapy.Field()
    restaurant_id = scrapy.Field()

