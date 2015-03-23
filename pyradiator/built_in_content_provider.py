import os
import random

from common import execute_simple_command
from common import execute_compound_command


class AskTheCow(object):

    def __init__(self):
        self.cows = ["-b", "-d", "-g", "-p", "-s", "-t", "-w", "-y"]

    def __call__(self):
        return execute_compound_command(
            ["fortune", "-s"], ["cowsay", random.choice(self.cows)]
        )


class AskTop(object):

    def __call__(self):
        return execute_simple_command(
            ["top", "-H", "-b", "-n1", "-p", str(os.getppid())]
        )


class AskW(object):

    def __call__(self):
        return execute_simple_command(["w", "-s"])


class AskFinger(object):

    def __call__(self):
        return execute_simple_command(["finger", os.getlogin()])
