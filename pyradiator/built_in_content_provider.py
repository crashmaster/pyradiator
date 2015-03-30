import os
import re
import random

from common import execute_simple_command
from common import execute_compound_command
from common import ColoredString


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


class AskTop(object):

    def __call__(self):
        return [
            [ColoredString(x)] for x in
            execute_simple_command([
                "top",
                "-H",
                "-b",
                "-n1",
                "-p", str(os.getppid())
            ])
        ]


class AskW(object):

    def __call__(self):
        return [
            [ColoredString(x)] for x in
            execute_simple_command([
                "w",
                "-s"
            ])
        ]


class AskFinger(object):

    def __init__(self, login_name):
        self.login_name = login_name
        self.login_name_pattern = re.compile("(.*)({})(.*)".
                                             format(self.login_name))

    def __call__(self):
        text = []
        for line in execute_simple_command(["finger", self.login_name]):
            hit = self.login_name_pattern.match(line)
            if hit:
                text.append([ColoredString(hit.group(1)),
                             ColoredString(hit.group(2), (255, 0, 0)),
                             ColoredString(hit.group(3))])
            else:
                text.append([ColoredString(line)])
        return text
