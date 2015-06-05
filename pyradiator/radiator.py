import contextlib
import logging
import random

import pygame

from pyradiator.app_state import ApplicationState
from pyradiator.command_line_args import get_configuration
from pyradiator.command_line_args import is_quiet_mode
from pyradiator.common import PrintText
from pyradiator.common import create_font
from pyradiator.common import print_loading_screen
from pyradiator.content_providers.content_provider_loader import load_content_provider
from pyradiator.radiator_channel import RadiatorChannel


LOG_LEVEL = logging.ERROR if is_quiet_mode() else logging.DEBUG
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


def create_main_surface(config):
    pygame.display.set_caption(config.window_title)
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
    shows = get_configured_shows(config)
    return [
        create_channel(config, subsurfaces[i], random.choice(shows))
        for i in range(config.number_of_left_rows + config.number_of_right_rows)
    ]


def get_configured_shows(config):
    return [
        (
            load_content_provider(name),
            properties["args"],
            properties["name"],
            properties["font_size"],
            properties["update_period"]
        ) for name, properties in config.channels.items()
    ]


def create_channel(config, subsurface, show):
    return RadiatorChannel(
        config=config,
        name=show[2],
        surface=subsurface,
        input_functor=show[0](**show[1]),
        output_functor=PrintText(config=config,
                                 surface=subsurface,
                                 position=(0, 0),
                                 font=create_font(config, show[3])),
        update_period=show[4]
    )


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
    config = get_configuration()

    main_surface = create_main_surface(config)
    subsurfaces = create_sub_surfaces(config, main_surface)

    print_loading_screen(config, main_surface)
    main_surface.fill(config.main_surface_color)

    channels = create_channels(config, subsurfaces)

    with turn_on_channels(application_state, channels):
        loop(application_state, config, subsurfaces, channels)
