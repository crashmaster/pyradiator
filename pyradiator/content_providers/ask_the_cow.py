import random

from pyradiator.common import ColoredString
from pyradiator.execute_command import execute_compound_command


class AskTheCow(object):

    def __init__(self):
        self.cows = ["-b", "-d", "-g", "-p", "-s", "-t", "-w", "-y"]

    def __call__(self):
        return [
            [ColoredString(x)] for x in
            execute_compound_command(
                ["fortune", "-s"],
                ["cowsay", random.choice(self.cows)])
        ]
