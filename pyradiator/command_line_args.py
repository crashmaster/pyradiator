import argparse
import collections
import sys

import pygame


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
COLORS = collections.OrderedDict([
    ("white", WHITE),
    ("black", BLACK),
    ("gray", GRAY),
])


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


class StoreColor(argparse.Action):
    def __call__(self, parser, namespace, value, option_string):
        setattr(namespace, self.dest, COLORS[value])


def parse_arguments(display_info):
    parser = argparse.ArgumentParser(
        description="THE Radiator.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--fullscreen",
        action="store_true",
        default=False,
        help="Display radiator in fullscreen mode."
    )
    parser.add_argument(
        "--window-width",
        type=int,
        default=int(display_info.current_w),
        action=StoreSize,
        const=display_info.current_w,
        help="Width in pixels of the radiator."
    )
    parser.add_argument(
        "--window-height",
        type=int,
        action=StoreSize,
        const=display_info.current_h,
        default=int(display_info.current_h),
        help="Height in pixels of the radiator."
    )
    parser.add_argument(
        "--margin-size",
        type=int,
        action=StoreSize,
        const=50,
        default=5,
        help="Margin size in pixels of the surfaces."
    )
    parser.add_argument(
        "--main-surface-color",
        action=StoreColor,
        default=BLACK,
        choices=COLORS.keys(),
        help="Color of the main surfaces."
    )
    parser.add_argument(
        "--sub-surface-color",
        action=StoreColor,
        default=BLACK,
        choices=COLORS.keys(),
        help="Color of the sub-surfaces."
    )
    parser.add_argument(
        "--static-fg-color",
        action=StoreColor,
        default=GRAY,
        choices=COLORS.keys(),
        help="Foreground color of the no-signal static noise."
    )
    parser.add_argument(
        "--static-bg-color",
        action=StoreColor,
        default=BLACK,
        choices=COLORS.keys(),
        help="Background color of the no-signal static noise."
    )
    parser.add_argument(
        "--font",
        type=str,
        action=StoreFont,
        default=pygame.font.get_default_font(),
        help="Font of the output-text. List system fonts with 'list' value."
    )
    parser.add_argument(
        "--font-size",
        type=int,
        default=20,
        help="Font-size of the output-text."
    )
    parser.add_argument(
        "--font-bold",
        action="store_true",
        default=False,
        help="Font of the output text is bold."
    )
    parser.add_argument(
        "--font-italic",
        action="store_true",
        default=False,
        help="Font of the output text is italic."
    )
    parser.add_argument(
        "--font-fg-color",
        action=StoreColor,
        default=WHITE,
        choices=COLORS.keys(),
        help="Foreground color of the fonts."
    )
    parser.add_argument(
        "--font-bg-color",
        action=StoreColor,
        default=BLACK,
        choices=COLORS.keys(),
        help="Background color of the fonts."
    )
    return parser.parse_args()
