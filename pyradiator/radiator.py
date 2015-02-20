import argparse
import collections
import logging
import sys

import pygame

IS_HELP_MODE = any(x in sys.argv for x in ["-h", "--help"])
LOG_LEVEL = logging.ERROR if IS_HELP_MODE else logging.DEBUG
FORMAT = "%(asctime)-15s %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=LOG_LEVEL)

LOGGER = logging.getLogger("watrad")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = collections.OrderedDict([
    ("white", (WHITE)),
    ("black", (BLACK)),
])


def initialize_pygame_modules():
    pygame.display.init()
    LOGGER.debug("pygame.display module initialized")
    pygame.font.init()
    LOGGER.debug("pygame.font module initialized")


def get_display_info():
    display_info = pygame.display.Info()
    LOGGER.debug("Display info: \n{}".format(display_info).rstrip())
    return display_info


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


def parse_arguments(display_info):
    parser = argparse.ArgumentParser(
        description="THE Radiator.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--window-width",
                        type=int,
                        default=int(display_info.current_w),
                        action=StoreSize,
                        const=display_info.current_w,
                        help="Width in pixels of the main window.")
    parser.add_argument("--window-height",
                        type=int,
                        action=StoreSize,
                        const=display_info.current_h,
                        default=int(display_info.current_h),
                        help="Height in pixels of the main window.")
    parser.add_argument("--margin-size",
                        type=int,
                        action=StoreSize,
                        const=50,
                        default=5,
                        help="Margin size in pixels of the surfaces.")
    parser.add_argument("--surface-fg-color",
                        default="white",
                        choices=["white", "black"],
                        help="Foreground color of the surfaces.")
    parser.add_argument("--surface-bg-color",
                        default="black",
                        choices=["white", "black"],
                        help="Background color of the surfaces.")
    parser.add_argument("--font-fg-color",
                        default="white",
                        choices=["white", "black"],
                        help="Foreground color of the fonts.")
    parser.add_argument("--font-bg-color",
                        default="black",
                        choices=["white", "black"],
                        help="Background color of the fonts.")
    return parser.parse_args()


def create_main_surface(args):
    resolution = (args.window_width, args.window_height)
    flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    main_surface = pygame.display.set_mode(resolution, flags)
    main_surface.fill(COLORS[args.surface_bg_color])
    LOGGER.debug("Main surface with resolution: {} created".
                 format(resolution))
    return main_surface


def create_sub_surface(args, main_surface, x, y, width, height):
    sub_surface = main_surface.subsurface((x, y, width, height))
    sub_surface.fill(COLORS[args.surface_fg_color])
    LOGGER.debug("Sub surface with resolution: {} @ {} created".
                 format((width, height), (x, y)))
    return sub_surface


def create_sub_surfaces(args, main_surface):
    quarter_width = int(args.window_width / 2)
    quarter_height = int(args.window_height / 2)
    return [
        create_sub_surface(args, main_surface,
                           args.margin_size + i * quarter_width,
                           args.margin_size + j * quarter_height,
                           quarter_width - (2 * args.margin_size),
                           quarter_height - (2 * args.margin_size))
        for i in range(2) for j in range(2)
    ]


def loop():
    fps = 60
    display_refresh = pygame.USEREVENT
    pygame.time.set_timer(display_refresh, int(1000.0 / fps))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                running = False
            elif event.type == display_refresh:
                pygame.display.flip()
        pygame.time.wait(0)


def main():
    initialize_pygame_modules()
    display_info = get_display_info()
    args = parse_arguments(display_info)
    main_surface = create_main_surface(args)
    create_sub_surfaces(args, main_surface)
    loop()

sys.exit(main())
