# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from datetime import time
import locale
import logging
import re

import scrapy
from itemloaders.processors import TakeFirst


def parse_time(values):
    for value in values:
        # Expecting a single hour like this: "4" or "15"
        match_time = re.match(r'^(\d+)$', value)

        # Expecting a time interval string like this: "04:15-04:30"
        # Exceptions:
        #   - 26.10.2025: There are times like this: 02a:15-02a:30 or 02b:00-02b:15
        match_time_interval = re.match(r'^(\d\d)[ab]?:(\d\d)-(\d\d)[ab]?:(\d\d)$', value)
        if match_time is not None:
            # The "- 1" is because the time given is the ending time; values
            # start with 1 (representing interval 00:00 - 01:00) and end with 24
            # (interval 23:00 - 00:00 next day)
            yield time(int(match_time[1]) - 1, 0)
        elif match_time_interval is not None:
            yield time(int(match_time_interval[1]), int(match_time_interval[2]))
        else:
            logging.warning(f"Invalid value, expecting number (hour) or time interval: {value}")



def parse_price(values):
    locale.setlocale(locale.LC_NUMERIC, 'cs_CZ.UTF-8')
    return [locale.atof(value.replace(' ', '')) for value in values]


class DayMarketPricesItem(scrapy.Item):
    date = scrapy.Field(output_processor=TakeFirst())
    time = scrapy.Field(input_processor=parse_time, output_processor=TakeFirst())
    price = scrapy.Field(input_processor=parse_price, output_processor=TakeFirst())
