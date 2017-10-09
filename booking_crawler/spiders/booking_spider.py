import datetime

import pymongo
from scrapy.spider import Spider
from scrapy import Request
import re
import logging

from ..items import BookingHotel

client = pymongo.MongoClient()
all_urls = set([elt["url"] for elt in list(client["booking"]["hotel"].find({}, {"url": 1}))])

class BookingSpider(Spider):
    name = "Booking"
    allowed_domains = ["booking.com"]

    start_urls = ['http://www.booking.com/destination.html']

    def parse(self, response):
        countries = response.css(".dest-sitemap__continent-item .dest-sitemap__country a::attr(href)").extract()
        for elt in countries:
            yield Request(url=response.urljoin(elt), callback=self.parse_country)

    def parse_country(self, response):
        cities = response.css(".general a::attr(href)").extract()
        for city in cities:
            yield Request(url=response.urljoin(city), callback=self.parse_city)

    def parse_city(self, response):
        hotels = response.css(".general tr a::attr(href)").extract()
        for hotel in hotels:
            if "/hotel" in hotel:
                country_code = response.url.split("/")[5]
                url_ = response.urljoin(hotel)
                if url_ not in all_urls :
                    yield Request(url=url_, callback=self.parse_hotel, meta={"country": country_code})

    def parse_hotel(self, response):
        logging.info("Scrap : {}".format(response.url))
        hotel = BookingHotel()
        hotel["country"] = response.meta["country"]
        hotel["url"] = response.url
        hotel["description"] = " ".join(response.css(".hotel_description_wrapper_exp p::text").extract()).replace("\n",
                                                                                                                  " ").replace(
            "  ", " ")
        hotel["name"] = response.css(".hp__hotel-name::text").extract_first().replace("\n", " ").strip()
        hotel["crawled_at"] = datetime.datetime.now()
        hotel["address"] = response.css(".hp_address_subtitle::text").extract_first().replace("\n", " ").strip()
        try:
            hotel["rate"] = float(response.css(
                "#reviewFloater #js--hp-gallery-scorecard .review-score-badge::text").extract_first().replace("\n",
                                                                                                              "").replace(
                ",", "."))
        except:
            hotel["rate"] = None

        hotel["photos"] = response.css(".hp-gallery-slides img::attr(data-highres)").extract()
        hotel["facilities"] = set(
            response.css(".hp_desc_important_facilities .important_facility ::attr(data-name-en)").extract())
        hotel["_id"] = response.css(".hp-lists button::attr(data-hotel-id)").extract_first()
        string_loc = response.css(".map_static_zoom::attr(style)").extract_first()
        try:
            finded = re.findall(r'\&center=(\d+\.\d+),[-]{0,1}(\d+\.\d+)\&size=', string_loc)[0]
            hotel["lat"] = float(finded[0])
            hotel["lon"] = float(finded[1])
        except:
            pass

        pois = []
        for poi in response.css(".poi-list-item"):
            name = poi.css(".poi-list-item__name::text").extract()
            title = poi.css(".poi-list-item__title::text").extract()
            distance = poi.css(".poi-list-item__distance::text").extract_first()

            pois.append({
                "name": "".join([elt for elt in title + name if elt != "\n"]),
                "distance": distance
            })

        hotel["facilities"].update(response.css(".facilitiesChecklist ul li::attr(data-name-en)").extract())
        hotel["facilities"] = list(hotel["facilities"])

        yield Request(url=response.urljoin(response.css(".show_all_reviews_btn::attr(href)").extract_first()),
                      callback=self.parse_comments, meta={"hotel": hotel})

    def parse_comments(self, response):
        hotel = response.meta["hotel"]
        hotel["reviews"] = []
        for review in response.css(".review_item_review"):
            negativ = review.css(".review_neg span::text").extract()
            positiv = review.css(".review_pos span::text").extract()
            score = float(review.css(".review-score-badge::text").extract_first().replace("\n", "").replace(",", "."))
            title = review.css(".review_item_header_content_container span::text").extract()
            doc = {
                "score": score,
                "title": title
            }
            if len(negativ) > 0 : doc['negativ'] = " ".join(negativ).strip()
            if len(positiv) > 0 : doc['positiv'] = " ".join(positiv).strip()
            #if len(negativ) > 0 : doc['negativ']: negativ).strip()
            #if len(positiv) > 0 : doc['positiv']: positiv).strip()

            hotel["reviews"].append(doc)

        yield hotel
