import os

from pyradiator.common import ColoredString
from pyradiator.common import execute_simple_command
from pyradiator.content_providers.ask_x import AskX


class AskTop(AskX):

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
