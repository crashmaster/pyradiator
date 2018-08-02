import argparse
import collections
import json
import logging
import operator
import os
import re
import sys

import pygame


LOGGER = logging.getLogger(__name__)
DISPLAY_INFO = None
DEFAULT_CONFIG_FILE = "~/.config/pyradiator.json"


def is_quiet_mode():
    return any(x in sys.argv for x in ["-h", "--help", "list", "generate"])


def get_display_info():
    global DISPLAY_INFO
    if DISPLAY_INFO:
        return DISPLAY_INFO
    DISPLAY_INFO = pygame.display.Info()
    LOGGER.debug("Display info: \n%s", str(DISPLAY_INFO).rstrip())
    return DISPLAY_INFO


class CommandLineArgument(object):
    def __init__(self, name, help, default, type, action, choices, const):
        self.name = name
        self.help = help
        self.default = default
        self.type = type
        self.action = action
        self.choices = choices
        self.const = const
        self.__dict__ = {
            key: value for key, value in self.__dict__.items()
        }


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


class StoreChannels(argparse.Action):
    def __call__(self, parser, namespace, value, option_string):
        setattr(namespace, self.dest, json.loads(value))


class StoreColor(argparse.Action):
    def __call__(self, parser, namespace, value, option_string):
        setattr(namespace, self.dest, COLORS[value])


class StoreConfigFile(argparse.Action):
    def __call__(self, parser, namespace, value, option_string):
        self.generate_config_file_on_request(value)
        setattr(namespace, self.dest, value)

    @staticmethod
    def generate_config_file_on_request(value):
        if value == "generate":
            settings = get_config_file_factory_settings()
            print(
                bytes(
                    "{}".format(
                        json.dumps(settings, indent=4, sort_keys=True)
                    ),
                    'ascii'
                ).decode('unicode-escape')
            )
            sys.exit(0)


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


class InvalidScreenLayout(Exception):
    pass


class StoreScreenLayout(argparse.Action):
    def __call__(self, parser, namespace, value, option_string):
        self.verify_screen_layout(value)
        setattr(namespace, self.dest, value)

    @staticmethod
    def verify_screen_layout(value):
        format_pattern = re.compile(r"(\d)\+(\d)\+(\d)\+(\d)")
        if not format_pattern.match(value):
            raise InvalidScreenLayout(value)


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
    return sorted([
        CommandLineArgument(
            name="window-title",
            help="Title of the radiator window.",
            default="PyRadiator",
            type=str,
            action=None,
            choices=None,
            const=None,
        ),
        CommandLineArgument(
            name="fullscreen",
            help="Display radiator in fullscreen mode.",
            default=False,
            type=None,
            action="store_true",
            choices=None,
            const=None,
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
            const=None,
        ),
        CommandLineArgument(
            name="sub-surface-color",
            help="Color of the sub-surfaces.",
            default=BLACK,
            type=None,
            action=StoreColor,
            choices=COLORS.keys(),
            const=None,
        ),
        CommandLineArgument(
            name="static-fg-color",
            help="Foreground color of the no-signal static noise.",
            default=GRAY,
            type=None,
            action=StoreColor,
            choices=COLORS.keys(),
            const=None,
        ),
        CommandLineArgument(
            name="static-bg-color",
            help="Background color of the no-signal static noise.",
            default=BLACK,
            type=None,
            action=StoreColor,
            choices=COLORS.keys(),
            const=None,
        ),
        CommandLineArgument(
            name="font",
            help="Font of the output-text. "
                 "List system fonts with 'list' value.",
            default=pygame.font.get_default_font(),
            type=str,
            action=StoreFont,
            choices=None,
            const=None,
        ),
        CommandLineArgument(
            name="font-size",
            help="Font-size of the output-text.",
            default=20,
            type=int,
            action=None,
            choices=None,
            const=None,
        ),
        CommandLineArgument(
            name="font-bold",
            help="Font of the output text is bold.",
            default=False,
            type=None,
            action="store_true",
            choices=None,
            const=None,
        ),
        CommandLineArgument(
            name="font-italic",
            help="Font of the output text is italic.",
            default=False,
            type=None,
            action="store_true",
            choices=None,
            const=None,
        ),
        CommandLineArgument(
            name="font-fg-color",
            help="Foreground color of the fonts.",
            default=WHITE,
            type=None,
            action=StoreColor,
            choices=COLORS.keys(),
            const=None,
        ),
        CommandLineArgument(
            name="font-bg-color",
            help="Background color of the fonts.",
            default=BLACK,
            type=None,
            action=StoreColor,
            choices=COLORS.keys(),
            const=None,
        ),
        CommandLineArgument(    # TODO: True/False?
            name="font-antialias",
            help="Font of the output text is antialiased.",
            default=True,
            type=None,
            action="store_true",
            choices=None,
            const=None,
        ),
        CommandLineArgument(
            name="number-of-left-rows",
            help="Number of rows on the left side.",
            default=0,
            type=int,
            action=None,
            choices=[0, 1, 2, 3, 4],
            const=None,
        ),
        CommandLineArgument(
            name="number-of-right-rows",
            help="Number of rows on the right side.",
            default=0,
            type=int,
            action=None,
            choices=[0, 1, 2, 3, 4],
            const=None,
        ),
        CommandLineArgument(
            name="config-file",
            help="Configuration file path. "
                 "Generate config file with 'generate' value.",
            default=DEFAULT_CONFIG_FILE,
            type=str,
            action=StoreConfigFile,
            choices=None,
            const=None,
        ),
        CommandLineArgument(
            name="screen-layout",
            help="Layout of the radiator screen. Format: "
                 "Number of Header Rows + "
                 "Number of Middle Left Rows + "
                 "Number of Middle Right Rows + "
                 "Number of Footer Rows",
            default="0+2+2+0",
            type=str,
            action=StoreScreenLayout,
            choices=None,
            const=None,
        ),
        CommandLineArgument(
            name="channels",
            help="Available channels",
            default=json.dumps({
                "top": {
                    "content_provider": "ask_top",
                    "content_provider_args": {},
                    "surface_number": 0,
                    "font_size": None,
                    "update_period": 30,
                },
                "cowsay": {
                    "content_provider": "ask_the_cow",
                    "content_provider_args": {},
                    "surface_number": 1,
                    "font_size": None,
                    "update_period": 30,
                },
                "w": {
                    "content_provider": "ask_w",
                    "content_provider_args": {},
                    "surface_number": 2,
                    "font_size": None,
                    "update_period": 30,
                },
                "finger": {
                    "content_provider": "ask_finger",
                    "content_provider_args": {
                        "login_name": os.getlogin()
                    },
                    "surface_number": 3,
                    "font_size": None,
                    "update_period": 30,
                },
                "jenkins": {
                    "content_provider": "ask_jenkins_jobs_status",
                    "content_provider_args": {
                        "jobs": {
                            "url": None,
                            "job_names": []
                        }
                    },
                    "surface_number": 4,
                    "font_size": None,
                    "update_period": 30,
                },
            }),
            type=str,
            action=StoreChannels,
            choices=None,
            const=None,
        ),
    ], key=operator.attrgetter("name"))


def normalize_settings_types(settings):
    return json.loads(json.dumps(settings))


def get_complete_factory_settings():
    settings = normalize_settings_types({
        x.name.replace("-", "_"): x.default for x in
        get_command_line_arguments(get_display_info())
    })
    LOGGER.debug("Factory settings: \n%s", settings)
    return settings


def get_config_file_factory_settings():
    settings = get_complete_factory_settings()
    for option_to_omit in ["config_file"]:
        settings.pop(option_to_omit)
    return settings


def get_config_file_settings(command_line_settings):
    try:
        config_file_name = os.path.expanduser(command_line_settings["config_file"])
        with open(config_file_name, "r") as config_file:
            config_file_content = config_file.read()
        if config_file_content:
            settings = {
                k.replace("-", "_"): v
                for k, v in json.loads(config_file_content).items()
            }
            LOGGER.debug("Config file settings: \n%s", settings)
            return settings
        else:
            return {}
    except IOError:
        return {}


def get_command_line_settings():
    cli_args = get_command_line_arguments(get_display_info())
    settings = normalize_settings_types(vars(parse_command_line_arguments(cli_args)))
    LOGGER.debug("Command line settings: \n%s", settings)
    return settings


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
        kwargs = {k: v for k, v in vars(i).items() if v is not None}
        option_string = kwargs.pop("name")
        parser.add_argument("--{}".format(option_string), **kwargs)


def merge_settings(factory_settings, config_file_settings, command_line_settings):
    config_dict = merge_config_dicts(factory_settings, config_file_settings, command_line_settings)
    return config_dict_to_namespace(config_dict)


def merge_config_dicts(factory_settings, config_file_settings, command_line_settings):
    config_dict = factory_settings.copy()
    config_dict.update(config_file_settings)
    for key, value in command_line_settings.items():
        if value != factory_settings[key]:
            config_dict[key] = value
    return config_dict


def config_dict_to_namespace(config_dict):
    config_ns = argparse.Namespace()
    for k, v in config_dict.items():
        setattr(config_ns, k, v)
    return config_ns


def get_configuration():
    factory_settings = get_complete_factory_settings()
    command_line_settings = get_command_line_settings()
    config_file_settings = get_config_file_settings(command_line_settings)
    config = merge_settings(
        factory_settings,
        config_file_settings,
        command_line_settings
    )
    LOGGER.info("Configuration: \n%s", config)
    return config
