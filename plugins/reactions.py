from __future__ import print_function
from __future__ import unicode_literals
from rtmbot.core import Plugin

import re


class AutoReaction(Plugin):
    def __init__(self, name=None, slack_client=None, plugin_config=None):
        super(AutoReaction, self).__init__(name, slack_client, plugin_config)
        expr = "|".join([re.escape(word) for word in self.words])
        self.re_words = re.compile(r"\b(?:" + expr + r")+\b")

    def has_word(self, text):
        return self.re_words.search(text) is not None

    def process_message(self, data):
        if self.has_word(data.get("text").lower()):
            self.slack_client.api_call(
                "reactions.add",
                channel=data.get("channel"),
                timestamp=data.get("ts"),
                name=self.emoji)


# Oh that's pretty neat.
class AutoNeat(AutoReaction):
    words = ["neat"]
    emoji = "neat"


# Work, work.
class AutoWork(AutoReaction):
    words = ["work"]
    emoji = "zugzug"
