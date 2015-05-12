import argparse
import collections
import logging
import sys

import pygame

LOGGER = logging.getLogger(__name__)

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (180, 180, 180)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
COLORS = collections.OrderedDict([
    ("black", BLACK),
    ("blue", BLUE),
    ("gray", GRAY),
    ("green", GREEN),
    ("red", RED),
    ("white", WHITE),
    ("yellow", YELLOW),
])


def get_display_info():
    display_info = pygame.display.Info()
    LOGGER.debug("Display info: \n{}".format(display_info).rstrip())
    return display_info

DISPLAY_INFO = get_display_info()

CommandLineArgument = collections.namedtuple(
    "CommandLineArgument", [
        "name",
        "help",
        "default",
        "type",
        "action",
        "choices",
        "const"
    ]
)


class StoreColor(argparse.Action):
    def __call__(self, parser, namespace, value, option_string):
        setattr(namespace, self.dest, COLORS[value])


class StoreFont(argparse.Action):
    def __call__(self, parser, namespace, value, option_string):
        self.print_system_font_list_on_request(value)
        setattr(namespace, self.dest, value)

    @staticmethod
    def print_system_font_list_on_request(value):
        if value == "list":
            system_fonts = ", ".join(sorted(pygame.font.get_fonts()))
            print("Available system fonts: {}".format(system_fonts))
            sys.exit(0)


class StoreSize(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, const=None, **kwargs):
        if const is None:
            raise ValueError("const for '{}' not set".format(option_strings))
        super(StoreSize, self).__init__(
            option_strings, dest, nargs, const, **kwargs
        )

    def __call__(self, parser, namespace, value, option_string):
        if value > self.const:
            raise ValueError("'{}' too big, max: {}".
                             format(option_string, self.const))
        setattr(namespace, self.dest, value)


COMMAND_LINE_ARGUMENTS = [
    CommandLineArgument(
        name="--window-title",
        help="Title of the radiator window.",
        default="PyRadiator",
        type=str,
        action=None,
        choices=None,
        const=None
    ),
    CommandLineArgument(
        name="--fps",
        help="Expected frames per second for the radiator.",
        default=60,
        type=int,
        action=None,
        choices=None,
        const=None
    ),
    CommandLineArgument(
        name="--fullscreen",
        help="Display radiator in fullscreen mode.",
        default=False,
        type=None,
        action="store_true",
        choices=None,
        const=None
    ),
    CommandLineArgument(
        name="--window-width",
        help="Width in pixels of the radiator.",
        default=int(DISPLAY_INFO.current_w),
        type=int,
        action=StoreSize,
        choices=None,
        const=DISPLAY_INFO.current_w,
    ),
    CommandLineArgument(
        name="--window-height",
        help="Height in pixels of the radiator.",
        default=int(DISPLAY_INFO.current_h),
        type=int,
        action=StoreSize,
        choices=None,
        const=DISPLAY_INFO.current_h,
    ),
    CommandLineArgument(
        name="--margin-size",
        help="Margin size in pixels of the surfaces.",
        default=5,
        type=int,
        action=StoreSize,
        choices=None,
        const=50,
    ),
    CommandLineArgument(
        name="--main-surface-color",
        help="Color of the main surfaces.",
        default=BLACK,
        type=None,
        action=StoreColor,
        choices=COLORS.keys(),
        const=None
    ),
    CommandLineArgument(
        name="--sub-surface-color",
        help="Color of the sub-surfaces.",
        default=BLACK,
        type=None,
        action=StoreColor,
        choices=COLORS.keys(),
        const=None
    ),
    CommandLineArgument(
        name="--static-fg-color",
        help="Foreground color of the no-signal static noise.",
        default=GRAY,
        type=None,
        action=StoreColor,
        choices=COLORS.keys(),
        const=None
    ),
    CommandLineArgument(
        name="--static-bg-color",
        help="Background color of the no-signal static noise.",
        default=BLACK,
        type=None,
        action=StoreColor,
        choices=COLORS.keys(),
        const=None
    ),
    CommandLineArgument(
        name="--font",
        help="Font of the output-text. List system fonts with 'list' value.",
        default=pygame.font.get_default_font(),
        type=str,
        action=StoreFont,
        choices=None,
        const=None
    ),
    CommandLineArgument(
        name="--font-size",
        help="Font-size of the output-text.",
        default=20,
        type=int,
        action=None,
        choices=None,
        const=None
    ),
    CommandLineArgument(
        name="--font-bold",
        help="Font of the output text is bold.",
        default=False,
        type=None,
        action="store_true",
        choices=None,
        const=None
    ),
    CommandLineArgument(
        name="--font-italic",
        help="Font of the output text is italic.",
        default=False,
        type=None,
        action="store_true",
        choices=None,
        const=None
    ),
    CommandLineArgument(
        name="--font-fg-color",
        help="Foreground color of the fonts.",
        default=WHITE,
        type=None,
        action=StoreColor,
        choices=COLORS.keys(),
        const=None
    ),
    CommandLineArgument(
        name="--font-bg-color",
        help="Background color of the fonts.",
        default=BLACK,
        type=None,
        action=StoreColor,
        choices=COLORS.keys(),
        const=None
    ),
    CommandLineArgument(
        name="--font-antialias",
        help="Font of the output text is antialiased.",
        default=1,
        type=int,
        action=None,
        choices=[0, 1],
        const=None
    ),
    CommandLineArgument(
        name="--number-of-left-rows",
        help="Number of rows on the left side.",
        default=0,
        type=int,
        action=None,
        choices=[0, 1, 2, 3, 4],
        const=None
    ),
    CommandLineArgument(
        name="--number-of-right-rows",
        help="Number of rows on the right side.",
        default=0,
        type=int,
        action=None,
        choices=[0, 1, 2, 3, 4],
        const=None
    ),
]


def parse_command_line_arguments():
    parser = argparse.ArgumentParser(
        description="THE Radiator.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--window-title",
        help="Title of the radiator window.",
        default="PyRadiator",
        type=str,
    )
    parser.add_argument(
        "--fps",
        help="Expected frames per second for the radiator.",
        default=60,
        type=int,
    )
    parser.add_argument(
        "--fullscreen",
        help="Display radiator in fullscreen mode.",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--window-width",
        help="Width in pixels of the radiator.",
        default=int(DISPLAY_INFO.current_w),
        type=int,
        action=StoreSize,
        const=DISPLAY_INFO.current_w,
    )
    parser.add_argument(
        "--window-height",
        help="Height in pixels of the radiator.",
        default=int(DISPLAY_INFO.current_h),
        type=int,
        action=StoreSize,
        const=DISPLAY_INFO.current_h,
    )
    parser.add_argument(
        "--margin-size",
        help="Margin size in pixels of the surfaces.",
        default=5,
        type=int,
        action=StoreSize,
        const=50,
    )
    parser.add_argument(
        "--main-surface-color",
        help="Color of the main surfaces.",
        default=BLACK,
        action=StoreColor,
        choices=COLORS.keys(),
    )
    parser.add_argument(
        "--sub-surface-color",
        help="Color of the sub-surfaces.",
        default=BLACK,
        action=StoreColor,
        choices=COLORS.keys(),
    )
    parser.add_argument(
        "--static-fg-color",
        help="Foreground color of the no-signal static noise.",
        default=GRAY,
        action=StoreColor,
        choices=COLORS.keys(),
    )
    parser.add_argument(
        "--static-bg-color",
        help="Background color of the no-signal static noise.",
        default=BLACK,
        action=StoreColor,
        choices=COLORS.keys(),
    )
    parser.add_argument(
        "--font",
        help="Font of the output-text. List system fonts with 'list' value.",
        default=pygame.font.get_default_font(),
        type=str,
        action=StoreFont,
    )
    parser.add_argument(
        "--font-size",
        help="Font-size of the output-text.",
        default=20,
        type=int,
    )
    parser.add_argument(
        "--font-bold",
        help="Font of the output text is bold.",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--font-italic",
        help="Font of the output text is italic.",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--font-fg-color",
        help="Foreground color of the fonts.",
        default=WHITE,
        action=StoreColor,
        choices=COLORS.keys(),
    )
    parser.add_argument(
        "--font-bg-color",
        help="Background color of the fonts.",
        default=BLACK,
        action=StoreColor,
        choices=COLORS.keys(),
    )
    parser.add_argument(
        "--font-antialias",
        help="Font of the output text is antialiased.",
        default=1,
        type=int,
        choices=[0, 1],
    )
    parser.add_argument(
        "--number-of-left-rows",
        help="Number of rows on the left side.",
        default=0,
        type=int,
        choices=[0, 1, 2, 3, 4],
    )
    parser.add_argument(
        "--number-of-right-rows",
        help="Number of rows on the right side.",
        default=0,
        type=int,
        choices=[0, 1, 2, 3, 4],
    )
    return parser.parse_args()


def get_configuration():
    return parse_command_line_arguments()
