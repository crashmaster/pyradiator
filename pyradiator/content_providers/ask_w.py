from pyradiator.common import ColoredString
from pyradiator.common import execute_simple_command


class AskW(object):

    def __call__(self):
        return [
            [ColoredString(x)] for x in
            execute_simple_command([
                "w",
                "-s"
            ])
        ]
