from pyradiator.common import ColoredString
from pyradiator.common import execute_simple_command
from pyradiator.content_providers.ask_x import AskX


class AskW(AskX):

    def __call__(self):
        return [
            [ColoredString(x)] for x in
            execute_simple_command([
                "w",
                "-s"
            ])
        ]
