from datetime import date
from urllib.parse import urlencode

import scrapy
from dateutil import rrule
from scrapy.loader import ItemLoader

from ..items import DayMarketPricesItem


class DayMarketPricesSpider(scrapy.Spider):
    name = "day_market_prices_spider"

    def __init__(self, date_from, date_to=None, cb_item_scraped=None, *args, **kwargs):
        """ Get the electricity prices from OTE. It will scrape the OTE website
            and get daily electricity price for the given interval specified by
            `date_from` and `date_to` (which are datetime.date-compatible
            objects). If `date_to` is not provided it will scrape data starting
            from `date_from` till today.

            The `cb_item_scraped` is a callback accepting one argument "item"
            that will be called for each item (consumption data for the given
            month) scraped.
        """
        super().__init__(*args, **kwargs)

        # Year/month to scrape
        self._date_from = date_from
        self._date_to = date_to if date_to is not None else date.today()

    async def start(self):
        # Iterate over years/months between `date_from` and `date_to` and get
        # the hourly prices for the respective days.
        #
        # We need to set the day in `dtstart` to the first day of month because
        # otherwise if the day is greater than the day in `until` the last
        # month would not be included. For example for dtstart 2020-03-09 and
        # until 2020-08-01 would skip 2020-08 because 2020-08-09 comes after
        # 2020-08-01.
        for dt in rrule.rrule(rrule.DAILY, dtstart=self._date_from, until=self._date_to):
            dt = dt.date()
            qs = urlencode(
                {
                    "date": dt.isoformat(),
                    "time_resolution": "PT15M" # PT15M: 15m; PT60M: 1h
                }
            )
            url = f"https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh?{qs}"
            yield scrapy.Request(url=url, callback=self.handle_day_market_prices, cb_kwargs={"dt": dt})

    def handle_day_market_prices(self, response, dt):
        table_rows = response.css("div.report_content > div.bigtable table.report_table tbody tr")
        for row in table_rows[:-1]:
            loader = ItemLoader(item=DayMarketPricesItem(), selector=row)
            loader.add_value("date", dt)
            if row.css("th"):
                loader.add_css("time", "th::text")
                loader.add_css("price", "td::text")
            else:
                loader.add_css("time", "td:nth-child(1)::text")
                loader.add_css("price", "td:nth-child(2)::text")
            item = loader.load_item()

            yield item
