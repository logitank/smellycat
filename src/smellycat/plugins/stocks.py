import time
import requests

from collections import defaultdict
from operator import itemgetter
from rtmbot.core import Plugin

# It's an all out war!
class StockLeaders(Plugin):
    def __init__(self, name=None, slack_client=None, plugin_config=None):
        super(StockLeaders, self).__init__(name, slack_client, plugin_config)
        self.symbols = ["aapl", "goog", "nflx"]
        self.triggers = {"apple", "aapl", "netflix", "nflx", "google", "goog"}
        # Maintain per-channel cooldown to prevent spammy bot behavior/abuse.
        self.last_announced = defaultdict(int)
        self.rate_limit_seconds = 60

    def process_message(self, data):
        channel, text = data.get("channel", ""), data.get("text", "")
        if not self.is_rate_limited(channel) and self.has_match(text):
            # Get the stocks and sort them by price change descending.
            stocks = sorted(get_stocks(self.symbols), key=itemgetter("change_pct"), reverse=True)
            # Announce stock prices to channel and start 60 second cooldown.
            msg = "\n".join([self.format_stock_line(s) for s in stocks])
            self.outputs.append([channel, msg])
            self.last_announced[channel] = self.now()

    def has_match(self, msg):
        # We ignore actual stock price queries.
        if msg and not msg.startswith("$$"):
            # Return true if any of these words are a trigger.
            trigger_matches = set(msg.lower().split()) & self.triggers
            return bool(trigger_matches)

    def is_rate_limited(self, channel):
        return self.now() - self.last_announced[channel] < self.rate_limit_seconds

    @staticmethod
    def format_stock_line(stock):
        return "> :{symbol}: _{change_pct:+0.5f}_ at ${price:,.2f}".format(**stock)

    @staticmethod
    def now():
        return int(time.time())


# Handle stock price requests of the form "$$ SYMBOL1 SYMBOL2 ...".
class StockPrices(Plugin):
    def process_message(self, data):
        channel = data.get("channel", "")
        text = data.get("text", "")
        if self.has_match(text):
            # Fetch and sort stocks by market cap, descending.
            symbols = text[2:].split()
            stocks = sorted(get_stocks(symbols), key=itemgetter("market_cap"), reverse=True)
            # Announce these ordered stock prices to the channel.
            msg = "\n".join([self.format_stock_line(s) for s in stocks])
            self.outputs.append([channel, msg])

    @staticmethod
    def has_match(msg):
        return msg.startswith("$$")

    @staticmethod
    def format_stock_line(stock):
        return "> {name}, at ${price:,.2f}, total ${market_cap:,.0f}".format(**stock)


# Get stock price info for a list of stock symbols.
def get_stocks(symbols):
    # Fetch from IEX free batch API.
    iex_url = "https://api.iextrading.com/1.0/stock/market/batch"
    res = requests.get(iex_url, params={"symbols": ",".join(symbols), "types": "quote"})
    res.raise_for_status()
    # Parse JSON response to a list of dicts for each symbol.
    quotes = res.json().items()
    stocks = [
        {
            "symbol": symbol.lower(),
            "name": data["quote"]["companyName"],
            "price": data["quote"]["latestPrice"],
            "market_cap": data["quote"]["marketCap"],
            "change_pct": data["quote"]["changePercent"],
        }
        for symbol, data in quotes
    ]
    return stocks
