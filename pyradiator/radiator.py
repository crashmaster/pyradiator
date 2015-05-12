import os
import contextlib
import logging
import random
import sys

import pygame

from pyradiator.app_state import ApplicationState
from pyradiator.command_line_args import get_configuration
from pyradiator.common import PrintText
from pyradiator.common import create_font
from pyradiator.common import print_loading_screen
from pyradiator.content_providers.content_provider_loader import load_content_provider
from pyradiator.radiator_channel import RadiatorChannel


IS_HELP_MODE = any(x in sys.argv for x in ["-h", "--help", "list"])

LOG_LEVEL = logging.ERROR if IS_HELP_MODE else logging.DEBUG
FORMAT = "%(asctime)-15s %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=LOG_LEVEL)
LOGGER = logging.getLogger(__name__)


def initialize_pygame_modules():
    pygame.display.init()
    LOGGER.debug("Module pygame.display initialized")
    pygame.font.init()
    LOGGER.debug("Module pygame.font initialized")


def disable_mouse_events():
    pygame.event.set_blocked(pygame.MOUSEMOTION)
    pygame.event.set_blocked(pygame.MOUSEBUTTONUP)
    pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
    LOGGER.debug("Mouse-events: motion, button-up, button-down disabled")


def get_display_info():
    display_info = pygame.display.Info()
    LOGGER.debug("Display info: \n{}".format(display_info).rstrip())
    return display_info


def create_main_surface(config):
    pygame.display.set_caption(config.title)
    resolution = (config.window_width, config.window_height)
    flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    if config.fullscreen:
        flags |= pygame.FULLSCREEN
        LOGGER.debug("Fullscreen mode enabled")
    main_surface = pygame.display.set_mode(resolution, flags)
    LOGGER.debug("Main surface with resolution: {} created".
                 format(resolution))
    return main_surface


def get_rows_per_column(config):
    if config.number_of_left_rows == config.number_of_right_rows == 0:
        raise RuntimeError("number_of_left_rows == number_of_right_rows == 0")

    rows_per_column = []
    if config.number_of_left_rows > 0:
        rows_per_column.append(config.number_of_left_rows)
    if config.number_of_right_rows > 0:
        rows_per_column.append(config.number_of_right_rows)
    return rows_per_column


def create_sub_surface(config, main_surface, x, y, width, height):
    sub_surface = main_surface.subsurface((x, y, width, height))
    LOGGER.debug("Sub surface with resolution: {} @ {} created".
                 format((width, height), (x, y)))
    return sub_surface


def create_sub_surfaces(config, main_surface):
    rows_per_column = get_rows_per_column(config)
    surface_width = int(config.window_width / len(rows_per_column))

    return [
        create_sub_surface(
            config,
            main_surface,
            config.margin_size + column * surface_width,
            config.margin_size + row * int(config.window_height / rows_per_column[column]),
            surface_width - (2 * config.margin_size),
            int(config.window_height / rows_per_column[column]) - (2 * config.margin_size)
        )
        for column in range(len(rows_per_column))
        for row in range(rows_per_column[column])
    ]


def loop(application_state, config, subsurfaces, channels):
    clock = pygame.time.Clock()
    LOGGER.debug("Enter main loop")
    application_state.set_application_state(application_state.MAIN_LOOP)
    while application_state.running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                application_state.stop_main_loop()
            for channel in channels:
                if channel.no_signal():
                    channel.display_static(clock)
        pygame.display.flip()

        pygame.time.wait(0)


def create_channels(config, subsurfaces):
    shows = [
        ("top", load_content_provider("ask_top"), {}, None, 10),
        ("cowsay", load_content_provider("ask_the_cow"), {}, 26, 11),
        ("w", load_content_provider("ask_w"), {}, None, 12),
        ("finger", load_content_provider("ask_finger"), {"login_name": os.getlogin()}, None, 13),
    ]
    channels = []
    for i in range(config.number_of_left_rows + config.number_of_right_rows):
        show = random.choice(shows)
        input_functor = show[1](**show[2])
        output_functor = PrintText(config=config,
                                   surface=subsurfaces[i],
                                   position=(0, 0),
                                   font=create_font(config, show[3]))
        channels.append(
            RadiatorChannel(config=config,
                            name=show[0],
                            surface=subsurfaces[i],
                            input_functor=input_functor,
                            output_functor=output_functor,
                            update_period=show[4]))
    return channels


@contextlib.contextmanager
def turn_on_channels(application_state, channels):
    with application_state.suspend_signal_handling():
        for channel in channels:
            channel.turn_on()
    yield
    for channel in channels:
        channel.turn_off()


def main():
    application_state = ApplicationState()

    initialize_pygame_modules()
    disable_mouse_events()
    display_info = get_display_info()
    config = get_configuration(display_info)
    print config
    print vars(config)
    return

    main_surface = create_main_surface(config)
    subsurfaces = create_sub_surfaces(config, main_surface)

    print_loading_screen(config, main_surface)
    main_surface.fill(config.main_surface_color)

    channels = create_channels(config, subsurfaces)

    with turn_on_channels(application_state, channels):
        loop(application_state, config, subsurfaces, channels)
