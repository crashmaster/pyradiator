import re

from common import ColoredString
from common import execute_simple_command


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
