from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from booking_crawler.spiders.booking_spider import BookingSpider
from booking_crawler.spiders.tripadvisor_spider import TripAdvisorSpider

process = CrawlerProcess(get_project_settings())
process.crawl(TripAdvisorSpider)
process.crawl(BookingSpider)
process.start()