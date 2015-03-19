import logging
import os
import random
import sys

import pygame

from common import create_font
from common import execute_simple_command
from common import execute_compound_command
from common import print_loading_screen
from common import PrintText
from command_line_args import parse_arguments
from radiator_channel import RadiatorChannel


IS_HELP_MODE = any(x in sys.argv for x in ["-h", "--help", "list"])
LOG_LEVEL = logging.ERROR if IS_HELP_MODE else logging.DEBUG
FORMAT = "%(asctime)-15s %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=LOG_LEVEL)

LOGGER = logging.getLogger("radiator")


def initialize_pygame_modules():
    pygame.display.init()
    LOGGER.debug("pygame.display module initialized")
    pygame.font.init()
    LOGGER.debug("pygame.font module initialized")


def disable_mouse_events():
    pygame.event.set_blocked(pygame.MOUSEMOTION)
    pygame.event.set_blocked(pygame.MOUSEBUTTONUP)
    pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
    LOGGER.debug("Mouse-events disabled")


def get_display_info():
    display_info = pygame.display.Info()
    LOGGER.debug("Display info: \n{}".format(display_info).rstrip())
    return display_info


def create_main_surface(config):
    pygame.display.set_caption("PyRadiator by Crashmaster")
    resolution = (config.window_width, config.window_height)
    flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    if config.fullscreen:
        flags |= pygame.FULLSCREEN
        LOGGER.debug("Fullscreen mode enabled")
    main_surface = pygame.display.set_mode(resolution, flags)
    main_surface.fill(config.main_surface_color)
    LOGGER.debug("Main surface with resolution: {} created".
                 format(resolution))
    return main_surface


def create_sub_surface(config, main_surface, x, y, width, height):
    sub_surface = main_surface.subsurface((x, y, width, height))
    sub_surface.fill(config.sub_surface_color)
    LOGGER.debug("Sub surface with resolution: {} @ {} created".
                 format((width, height), (x, y)))
    return sub_surface


def create_sub_surfaces(config, main_surface):
    if config.number_of_left_rows == 0 and config.number_of_right_rows == 0:
        raise RuntimeError("number_of_left_rows == number_of_right_rows == 0")

    rows = []
    if config.number_of_left_rows > 0:
        rows.append(config.number_of_left_rows)
    if config.number_of_right_rows > 0:
        rows.append(config.number_of_right_rows)
    surface_width = int(config.window_width / len(rows))

    surfaces = []
    for i in range(len(rows)):
        for j in range(rows[i]):
            surface_height = int(config.window_height / rows[i])
            surfaces.append(create_sub_surface(
                config,
                main_surface,
                config.margin_size + i * surface_width,
                config.margin_size + j * surface_height,
                surface_width - (2 * config.margin_size),
                surface_height - (2 * config.margin_size)))
    return surfaces


def loop(config, subsurfaces, channels):
    display_refresh = pygame.USEREVENT
    pygame.time.set_timer(display_refresh, int(1000.0 / config.fps))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False
            elif event.type == display_refresh:
                pygame.display.flip()
            for channel in channels:
                if channel.no_signal():
                    channel.display_static()

        pygame.time.wait(0)


class AskTheCow(object):

    def __init__(self):
        self.cows = ["-b", "-d", "-g", "-p", "-s", "-t", "-w", "-y"]

    def __call__(self):
        return execute_compound_command(
            ["fortune", "-s"], ["cowsay", random.choice(self.cows)]
        )


class AskTop(object):

    def __call__(self):
        return execute_simple_command(
            ["top", "-H", "-b", "-n1", "-p", str(os.getppid())]
        )


class AskW(object):

    def __call__(self):
        return execute_simple_command(["w", "-s"])


class AskFinger(object):

    def __call__(self):
        return execute_simple_command(["finger", os.getlogin()])


def main():
    initialize_pygame_modules()
    disable_mouse_events()
    display_info = get_display_info()
    config = parse_arguments(display_info)

    main_surface = create_main_surface(config)
    subsurfaces = create_sub_surfaces(config, main_surface)

    print_loading_screen(config, main_surface)

    boo = [
        ("top", AskTop, 10),
        ("cowsay", AskTheCow, 15),
        ("w", AskW, 20),
        ("finger", AskFinger, 25),
    ]
    channels = []
    for i in range(config.number_of_left_rows + config.number_of_right_rows):
        tmp = random.choice(boo)
        channels.append(RadiatorChannel(config=config,
                                        name=tmp[0],
                                        surface=subsurfaces[i],
                                        input_functor=tmp[1](),
                                        output_functor=PrintText(config=config,
                                                                 surface=subsurfaces[i],
                                                                 position=(0, 0),
                                                                 font=create_font(config)),
                                        update_period=tmp[2]))

    main_surface.fill(config.main_surface_color)

    for channel in channels:
        channel.turn_on()

    loop(config, subsurfaces, channels)

    for channel in channels:
        channel.turn_off()


sys.exit(main())
