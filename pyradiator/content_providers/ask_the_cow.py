import random

from common import ColoredString
from common import execute_compound_command
from content_providers.ask_x import AskX


class AskTheCow(AskX):

    def __init__(self):
        self.cows = ["-b", "-d", "-g", "-p", "-s", "-t", "-w", "-y"]

    def __call__(self):
        return [
            [ColoredString(x)] for x in
            execute_compound_command(
                ["fortune", "-s"],
                ["cowsay", random.choice(self.cows)])
        ]
