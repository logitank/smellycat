import logging
import os
import yaml

from rtmbot import RtmBot


def main():
    # Logging config.
    log_fmt = "%(asctime)s - %(levelname)s - %(name)s - %(lineno)d - %(funcName)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_fmt)

    # Locate config and load from yaml.
    config_file = os.environ.get("BOT_CONFIG", "config.yaml")
    config = yaml.load(open(config_file, "r"))

    # Run the bot.
    bot = RtmBot(config)
    bot.start()
