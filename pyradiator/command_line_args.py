import argparse
import collections
import json
import logging
import os
import sys

import pygame

LOGGER = logging.getLogger(__name__)


def is_quiet_mode():
    return any(x in sys.argv for x in ["-h", "--help", "list", "generate"])


def get_display_info():
    display_info = pygame.display.Info()
    LOGGER.debug("Display info: \n{}".format(display_info).rstrip())
    return display_info


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


class StoreConfigFile(argparse.Action):
    def __call__(self, parser, namespace, value, option_string):
        self.generate_config_file_on_request(value)
        setattr(namespace, self.dest, value)

    @staticmethod
    def generate_config_file_on_request(value):
        if value == "generate":
            settings = get_config_file_factory_settings()
            print("{}".format(json.dumps(settings, indent=4, sort_keys=True)))
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


def get_command_line_arguments(display_info):
    return [
        CommandLineArgument(
            name="window-title",
            help="Title of the radiator window.",
            default="PyRadiator",
            type=str,
            action=None,
            choices=None,
            const=None
        ),
        CommandLineArgument(
            name="fps",
            help="Expected frames per second for the radiator.",
            default=60,
            type=int,
            action=None,
            choices=None,
            const=None
        ),
        CommandLineArgument(
            name="fullscreen",
            help="Display radiator in fullscreen mode.",
            default=False,
            type=None,
            action="store_true",
            choices=None,
            const=None
        ),
        CommandLineArgument(
            name="window-width",
            help="Width in pixels of the radiator.",
            default=int(display_info.current_w),
            type=int,
            action=StoreSize,
            choices=None,
            const=display_info.current_w,
        ),
        CommandLineArgument(
            name="window-height",
            help="Height in pixels of the radiator.",
            default=int(display_info.current_h),
            type=int,
            action=StoreSize,
            choices=None,
            const=display_info.current_h,
        ),
        CommandLineArgument(
            name="margin-size",
            help="Margin size in pixels of the surfaces.",
            default=5,
            type=int,
            action=StoreSize,
            choices=None,
            const=50,
        ),
        CommandLineArgument(
            name="main-surface-color",
            help="Color of the main surfaces.",
            default=BLACK,
            type=None,
            action=StoreColor,
            choices=COLORS.keys(),
            const=None
        ),
        CommandLineArgument(
            name="sub-surface-color",
            help="Color of the sub-surfaces.",
            default=BLACK,
            type=None,
            action=StoreColor,
            choices=COLORS.keys(),
            const=None
        ),
        CommandLineArgument(
            name="static-fg-color",
            help="Foreground color of the no-signal static noise.",
            default=GRAY,
            type=None,
            action=StoreColor,
            choices=COLORS.keys(),
            const=None
        ),
        CommandLineArgument(
            name="static-bg-color",
            help="Background color of the no-signal static noise.",
            default=BLACK,
            type=None,
            action=StoreColor,
            choices=COLORS.keys(),
            const=None
        ),
        CommandLineArgument(
            name="font",
            help="Font of the output-text. List system fonts with 'list' value.",
            default=pygame.font.get_default_font(),
            type=str,
            action=StoreFont,
            choices=None,
            const=None
        ),
        CommandLineArgument(
            name="font-size",
            help="Font-size of the output-text.",
            default=20,
            type=int,
            action=None,
            choices=None,
            const=None
        ),
        CommandLineArgument(
            name="font-bold",
            help="Font of the output text is bold.",
            default=False,
            type=None,
            action="store_true",
            choices=None,
            const=None
        ),
        CommandLineArgument(
            name="font-italic",
            help="Font of the output text is italic.",
            default=False,
            type=None,
            action="store_true",
            choices=None,
            const=None
        ),
        CommandLineArgument(
            name="font-fg-color",
            help="Foreground color of the fonts.",
            default=WHITE,
            type=None,
            action=StoreColor,
            choices=COLORS.keys(),
            const=None
        ),
        CommandLineArgument(
            name="font-bg-color",
            help="Background color of the fonts.",
            default=BLACK,
            type=None,
            action=StoreColor,
            choices=COLORS.keys(),
            const=None
        ),
        CommandLineArgument(
            name="font-antialias",
            help="Font of the output text is antialiased.",
            default=1,
            type=int,
            action=None,
            choices=[0, 1],
            const=None
        ),
        CommandLineArgument(
            name="number-of-left-rows",
            help="Number of rows on the left side.",
            default=0,
            type=int,
            action=None,
            choices=[0, 1, 2, 3, 4],
            const=None
        ),
        CommandLineArgument(
            name="number-of-right-rows",
            help="Number of rows on the right side.",
            default=0,
            type=int,
            action=None,
            choices=[0, 1, 2, 3, 4],
            const=None
        ),
        CommandLineArgument(
            name="config-file",
            help="Configuration file path. Generate config file with 'generate' value",
            default="~/.config/pyradiator",
            type=str,
            action=StoreConfigFile,
            choices=None,
            const=None
        ),
    ]


def get_complete_factory_settings():
    return {
        x.name: x.default for x in
        get_command_line_arguments(get_display_info())
    }


def get_config_file_factory_settings():
    settings = get_complete_factory_settings()
    for option_to_omit in ["config-file"]:
        settings.pop(option_to_omit)
    return settings


def get_config_file_settings():
    try:
        with open(os.path.expanduser("~/.config/pyradiator"), "r") as config_file:
            return json.loads(config_file.read())
    except IOError:
        return {}


def get_command_line_settings():
    command_line_arguments = get_command_line_arguments(get_display_info())
    return parse_command_line_arguments(command_line_arguments)


def parse_command_line_arguments(command_line_arguments):
    parser = create_command_line_argument_parser()
    add_command_line_arguments(parser, command_line_arguments)
    return parser.parse_args()


def create_command_line_argument_parser():
    return argparse.ArgumentParser(
        description="THE Radiator.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)


def add_command_line_arguments(parser, command_line_arguments):
    for i in command_line_arguments:
        kwargs = {k: v for k, v in vars(i).items() if v}
        option_string = kwargs.pop("name")
        parser.add_argument("--{}".format(option_string), **kwargs)


def get_configuration():
    # factory_settings = get_complete_factory_settings()
    # print("factory configuration", factory_settings)
    # config_file_settings = get_config_file_settings()
    # print("config file settings", config_file_settings)
    # command_line_settings = get_command_line_settings()
    # print("command line settings", command_line_settings)

    command_line_arguments = get_command_line_arguments(get_display_info())
    return parse_command_line_arguments(command_line_arguments)
