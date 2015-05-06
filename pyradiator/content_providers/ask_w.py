from common import ColoredString
from common import execute_simple_command
from content_providers.ask_x import AskX


class AskW(AskX):

    def __call__(self):
        return [
            [ColoredString(x)] for x in
            execute_simple_command([
                "w",
                "-s"
            ])
        ]
