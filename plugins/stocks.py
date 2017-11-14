from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
from rtmbot.core import Plugin

import time
import requests


# A special (the original) case of our StockPrices plugin, which announces
# AAPL and NFLX prices anytime Apple or Netflix are mentioned...
class AAPLvsNFLX(Plugin):
    def __init__(self, name=None, slack_client=None, plugin_config=None):
        super(AAPLvsNFLX, self).__init__(name, slack_client, plugin_config)
        self.last_announced = defaultdict(int)
        self.rate_limit = 5 # seconds
        self.triggers = set(["apple", "aapl", "netflix", "nflx"])

    def process_message(self, data):
        channel = data.get("channel", "")
        text = data.get("text", "")
        if self.has_match(text) and not self.is_rate_limited(channel):
            stocks = get_stocks("NFLX", "AAPL")
            aapl = stocks.get("AAPL", {})
            nflx = stocks.get("NFLX", {})
            msg = ":nflx: {} {} vs. :aapl: {} {}".format(
                self.get_emoji(nflx), nflx.get("price", "ERR"),
                self.get_emoji(aapl), aapl.get("price", "ERR"))
            self.outputs.append([channel, msg])
            self.last_announced[channel] = self.now()

    def has_match(self, msg):
        # We ignore actual stock price queries.
        if msg and not msg.startswith("$$"):
            words = set(msg.lower().split())
            return bool(words & self.triggers)

    def get_emoji(self, data):
        change = data.get("change")
        if change is None:
            return ":skull_and_crossbones:"
        elif float(change[1:]) < 0.0:
            return ":chart_with_downwards_trend:"
        else:
            return ":chart_with_upwards_trend:"

    def is_rate_limited(self, channel):
        return self.now() - self.last_announced[channel] < self.rate_limit

    def now(self):
        return int(time.time())


# Handle stock price requests of the form "$$ SYMBOL1 SYMBOL2 ...".
class StockPrices(Plugin):
    def process_message(self, data):
        channel = data.get("channel", "")
        text = data.get("text", "")
        if self.has_match(text):
            symbols = [sym.upper() for sym in text[2:].split()]
            stocks = get_stocks(*symbols)
            msg = "\n".join([
                "{name}: {price}, {market cap}".format(**stock)
                for stock in stocks.values()])
            self.outputs.append([channel, msg])

    def has_match(self, msg):
        return msg.startswith("$$")


# Get stock prices using IEX's free batch API.
def get_stocks(*symbols):
    all_symbols = ",".join(map(lambda x: x.lower(), symbols))
    iex_url = "https://api.iextrading.com/1.0/stock/market/batch"
    res = requests.get(iex_url, params={ "symbols": all_symbols, "types": "quote" })
    res.raise_for_status()
    stocks = {}

    for symbol, data in res.json().iteritems():
        quote = data["quote"]
        stocks[symbol] = {
            "change": "${:.2f}".format(float(quote["change"])),
            "price": "${:.2f}".format(float(quote["latestPrice"])),
            "market cap": "${:,}".format(quote["marketCap"]),
            "name": quote["companyName"]
        }

    return stocks
