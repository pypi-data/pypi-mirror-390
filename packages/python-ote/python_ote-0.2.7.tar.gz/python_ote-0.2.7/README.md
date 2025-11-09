# python-ote

Electricity prices scraper for OTE (ote-cr.cz)

## Install

```
pip install python-ote
```

In order to parse numbers corrently (Czech notation - e.g. 1,000,000) this
package needs the `cs_CZ.UTF-8` system locale. If the OS doesn't have it by default
the following commands can be used generate it:

```
echo "cs_CZ.UTF-8 UTF-8" >> /etc/locale.gen
locale-gen
```

## Usage

```
from ote import Ote
from dateutil import parser

# Create client
ote = Ote()
```

Use `getDayMarketPrices(date_from, date_to)` method to get electricity prices
for the given time range. It accepts a `date_from` and optionally a `date_to`,
both of which have to be a [datetime.date](https://docs.python.org/3/library/datetime.html#datetime.date)
object. If `date_to` is not specified the method returns data to today.

Examples:
```
# Get water consumption data from the specified date to now.
date_from = parser.parse('2020-08-01').date()
deferred_data = ote.getDayMarketPrices(date_from);

# Get water consumption data for a date interval
date_from = parser.parse('2020-08-01').date()
date_to = parser.parse('2020-08-11').date()
deferred_data = ote.getDayMarketPrices(date_from, date_to);

# Get water consumption data for a specific date (just 1 day)
date = parser.parse('2020-08-01').date()
deferred_data = ote.getDayMarketPrices(date, date);
```

You may call `getDayMarketPrices` multiple times with different parameters. It
returns a
[twisted.internet.defer.Deferred](https://twistedmatrix.com/documents/current/core/howto/defer.html)
object that can be used to retrieve the price data in the future using a
callback you need to provide.

```
def process_prices(prices)
  print(prices)

deferred_data.addCallback(process_prices)
```

If you have multiple `Deferred`s from multiple calls to `getDayMarketPrices`
you can use `Ote.join()` to get a `Deferred` that will be resolved after all
crawlers are finished.

The last callback should stop the reactor so it's shut down cleanly. Reactor
should be stopped after all crawlers are done so the `join()` method comes in
handy. Note that the reactor cannot be restarted so make sure this is the last
thing you do:

```
from twisted.internet import reactor

d = ote.join()
d.addBoth(lambda _: reactor.stop())
```

The last thing you need to do is run the reactor. The script will block until
the crawling is finished and all configured callbacks executed.

```
reactor.run(installSignalHandlers=False)
```

This might look a bit daunting so please see `test.py` for a complete example.

Keep in mind the library is using [Scrapy](https://scrapy.org) internally which
means it is scraping the OTE website. If OTE comes to think you are abusing the
website they may block your IP address.


# License

See [LICENSE](./LICENSE).
