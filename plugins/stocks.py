from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
from rtmbot.core import Plugin
from csv import DictReader
from cStringIO import StringIO

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
            msg = ":nflx: {} vs. :aapl: {}".format(
                stocks.get("NFLX", {}).get("price", "ERR"),
                stocks.get("AAPL", {}).get("price", "ERR"))
            self.outputs.append([channel, msg])
            self.last_announced[channel] = self.now()

    def has_match(self, msg):
        # We ignore actual stock price queries.
        if msg and not msg.startswith("$$"):
            words = set(msg.lower().split())
            return bool(words & self.triggers)

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


# Get stock prices using Yahoo's finance API.
def get_stocks(*symbols):
    stock_string = "+".join(map(lambda x: x.lower().replace(".", ""), symbols))
    yahoo_url = "https://download.finance.yahoo.com/d/quotes.csv"
    yahoo_format = ("j1"  # market cap
                    "l1"  # price
                    "n"   # name
                    "c1"  # change
                    )
    res = requests.get(yahoo_url, params={"s": stock_string, "f": yahoo_format})
    res.raise_for_status()
    data = DictReader(StringIO(res.content), fieldnames=["market cap", "price", "name", "change"])
    stocks = {}

    for sym, d in zip(symbols, data):
        if d["name"] == "N/A": # symbol not found
            continue
        stocks[sym] = {
            "price": "${:.2f}".format(float(d["price"])),
            "market cap": "${}".format(d["market cap"]),
            "name": d["name"]
        }

    return stocks
