from __future__ import print_function
from __future__ import unicode_literals
from rtmbot.core import Plugin

import re

# Oh that's pretty neat.
class AutoNeat(Plugin):
    def __init__(self, name=None, slack_client=None, plugin_config=None):
        super(AutoNeat, self).__init__(name, slack_client, plugin_config)
        self.re_neat = re.compile(r"\b(?:neat)+\b")

    def is_neat(self, text):
        return self.re_neat.search(text) is not None

    def process_message(self, data):
        if self.is_neat(data.get("text").lower()):
            self.slack_client.api_call("reactions.add",
                channel=data.get("channel"),
                timestamp=data.get("ts"),
                name="neat")
