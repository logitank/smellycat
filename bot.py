#!/usr/bin/env python

from argparse import ArgumentParser
import logging
import sys

from rtmbot import RtmBot
import yaml

log_fmt = "%(asctime)s - %(levelname)s - %(name)s - %(lineno)d - %(funcName)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_fmt)

def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '-c',
        '--config',
        help='Full path to config file.',
        metavar='path'
    )
    return parser.parse_args()

if __name__ == '__main__':
    # load args with config path
    args = parse_args()
    config = yaml.load(open(args.config or 'config.yaml', 'r'))
    bot = RtmBot(config)
    try:
        bot.start()
    except KeyboardInterrupt:
        sys.exit(0)
