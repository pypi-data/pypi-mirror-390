from datetime import datetime
from zoneinfo import ZoneInfo

from scrapy.settings import Settings
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from twisted.internet import defer

from .spiders.ote_electricity import DayMarketPricesSpider


class Ote:
    def __init__(self, log_enabled=None, log_level=None):
        # NOTE: We create settings "manually", not using
        # "scrapy.utils.project.get_project_settings" so we don't have to
        # bundle scrapy.cfg with the ote package.
        self._settings = Settings()
        self._settings.setmodule('ote.settings', priority='project')

        # Override settings if needed
        if log_enabled is not None:
            self._settings["LOG_ENABLED"] = log_enabled
        if log_level is not None:
            self._settings["LOG_LEVEL"] = log_level

    def getDayMarketPrices(self, date_from, date_to=None):
        """ Get electricity prices for the specified time period.  If `date_to`
            is not specified return consumption data from `date_from` till today.

            `date_from` and `date_to` must be datetime.date-compatible objects.

            Returns a `twisted.internet.defer.Deferred` that will return
        """
        prices = {}

        def _item_scraped(item):
            try:
                prices[datetime.combine(item["date"], item["time"], tzinfo=ZoneInfo('Europe/Prague')).isoformat()] = item["price"]
            except Exception as _:
                print(f"Processing scraped item failed: {item}")
                raise

        process = CrawlerProcess(self._settings)
        crawler = process.create_crawler(
            DayMarketPricesSpider
        )
        crawler.signals.connect(_item_scraped, signal=signals.item_scraped)

        process.crawl(crawler,
            date_from=date_from,
            date_to=date_to,
        )
        process.start()

        return prices
