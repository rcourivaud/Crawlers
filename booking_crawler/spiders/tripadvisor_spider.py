import datetime

from scrapy.spider import Spider
from scrapy.selector import HtmlXPathSelector
from scrapy import Request
import logging
import re

from ..items import TripAdvisorRestaurant


class TripAdvisorSpider(Spider):
    name = "TripAdvisor"
    allowed_domains = ["tripadvisor.fr"]

    #start_urls = ['https://www.tripadvisor.fr/Restaurants-g187070-France.html']
    start_urls = ['https://www.tripadvisor.fr/Restaurants-g187275-Germany.html',
                  'https://www.tripadvisor.fr/Restaurants-g187768-Italy.html',
                  'https://www.tripadvisor.fr/Restaurants-g186217-England.html',
                  'https://www.tripadvisor.fr/Restaurants-g188634-Belgium.html',
                  'https://www.tripadvisor.fr/Restaurants-g189100-Portugal.html'
                  'https://www.tripadvisor.fr/Restaurants-g187427-Spain.html',
                  'https://www.tripadvisor.fr/Restaurants-g188045-Switzerland.html',
                  'https://www.tripadvisor.fr/Restaurants-g188553-The_Netherlands.html',
                  'https://www.tripadvisor.fr/Restaurants-g274723-Poland.html',
                  'https://www.tripadvisor.fr/Restaurants-g189512-Denmark.html',
                  'https://www.tripadvisor.fr/Restaurants-g189806-Sweden.html',
                  'https://www.tripadvisor.fr/Restaurants-g190455-Norway.html',
                  'https://www.tripadvisor.fr/Hotels-g191-United_States-Hotels.html',
                  'https://www.tripadvisor.fr/Hotels-g255055-Australia-Hotels.html',
                  'https://www.tripadvisor.fr/Hotels-g294211-China-Hotels.html'
                  ]

    def parse(self, response):
        for city in response.css(".geo_wrap .geo_name a::attr(href)").extract():
            yield Request(url=response.urljoin(city), callback=self.parse_city)

        next_page = response.urljoin(response.css(".deckTools .unified .nav::attr(href)").extract_first())
        if next_page is not None:
            yield Request(url=next_page, callback=self.parse_nexts_pages)

    def parse_nexts_pages(self, response):
        for elt in response.css("#LOCATION_LIST .geoList li a::attr(href)").extract():
            yield Request(url=response.urljoin(elt), callback=self.parse_city)

        next_page = response.urljoin(response.css("#LOCATION_LIST .pgLinks a::attr(href)").extract()[-1])
        if next_page is not None:
            yield Request(url=next_page, callback=self.parse_nexts_pages)

    def parse_city(self, response):
        for elt in response.css("#EATERY_SEARCH_RESULTS .listing .title a::attr(href)").extract():
            yield Request(url=response.urljoin(elt), callback=self.parse_restaurant)

    def parse_restaurant(self, response):

        logging.info("Scrap : {}".format(response.url))

        restaurant = TripAdvisorRestaurant()
        restaurant["name"] = response.css("#HEADING::text").extract_first()
        restaurant["rate"] = float(response.css(".header_rating .rs .prw_rup .ui_bubble_rating::attr(content)").extract_first().replace(",", "."))
        restaurant["phone"] = response.css(".blEntry.phone span::text").extract_first()
        restaurant["photos"] = response.css(".carousel_images .page_images .prw_rup img::attr(data-src)").extract()
        restaurant["address"] = response.css(".blEntry.address .street-address::text").extract_first()
        restaurant["city"] = response.css(".blEntry.address .locality::text").extract_first()
        restaurant["country"] = response.css(".blEntry.address .country-name::text").extract_first()
        restaurant["crawled_at"] = datetime.datetime.now()
        ids = response.url.split("Review-")[1].split("-Reviews")[0].split("-")

        restaurant["loc_id"] = ids[0]
        restaurant["restaurant_id"] = ids[0]
        restaurant["_id"] = "".join(ids)
        restaurant["url"] = response.url



        restaurant["reviews"] = self.extract_reviews(response=response)

        """
        "&center=43.292839,5.371275&maptype="
        try:
            finded = re.findall(r'\&center=(\d+\.\d+),[-]{0,1}(\d+\.\d+)\&size=', string_loc)[0]
            restaurant["lat"] = float(finded[0])
            restaurant["lon"] = float(finded[1])
        except:
            pass
        """
        yield restaurant

    def extract_reviews(self, response):
        reviews = []
        for review in response.css("#taplc_location_reviews_list_0 .listContainer .review-container"):
            rate = review.css(".rating span::attr(class)").extract_first().split(" bubble_")[1]
            date = review.css(".rating .ratingDate::attr(title)").extract_first()
            text = review.css(".innerBubble .partial_entry::text").extract()
            reviews.append({
                "rate":float(rate),
                "date":date,
                "text":" ".join(text)
            })

        return reviews