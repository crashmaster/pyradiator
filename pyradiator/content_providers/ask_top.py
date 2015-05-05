import os

from common import ColoredString
from common import execute_simple_command


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
