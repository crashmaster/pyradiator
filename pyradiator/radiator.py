import logging
import math
import os
import random
import subprocess
import sys

import pygame

import command_line_args
from common import create_font
from radiator_channel import RadiatorChannel

PY3K = sys.version_info >= (3, 0)


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
    quarter_width = int(config.window_width / 2)
    quarter_height = int(config.window_height / 2)
    return [
        create_sub_surface(config, main_surface,
                           config.margin_size + i * quarter_width,
                           config.margin_size + j * quarter_height,
                           quarter_width - (2 * config.margin_size),
                           quarter_height - (2 * config.margin_size))
        for i in range(2) for j in range(2)
    ]


def loop(config, subsurfaces, channels):
    fps = 60
    display_refresh = pygame.USEREVENT
    pygame.time.set_timer(display_refresh, int(1000.0 / fps))
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


def execute_simple_command(command):
    try:
        proc = subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    except OSError:
        return
    else:
        if PY3K:
            return proc.communicate()[0].decode().split("\n")
        else:
            return proc.communicate()[0].split("\n")


def execute_compound_command(command_1, command_2):
    process_1 = subprocess.Popen(command_1,
                                 stdout=subprocess.PIPE)
    process_2 = subprocess.Popen(command_2,
                                 stdin=process_1.stdout,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
    process_1.stdout.close()
    if PY3K:
        return process_2.communicate()[0].decode().split("\n")
    else:
        return process_2.communicate()[0].split("\n")


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


class PrintText(object):

    def __init__(self, config, surface, position, font):
        self.config = config
        self.surface = surface
        self.position = position
        self.font = font
        self.font_antialias = True
        self.text_y_offset = math.ceil(self.font.get_height() * 1.05)

    def __call__(self, lines_to_print):
        if not lines_to_print:
            return

        self.surface.fill(self.config.sub_surface_color)
        position_x = self.position[0]
        position_y = self.position[1]
        for line in lines_to_print:
            rendered_line = self.font.render(line,
                                             self.font_antialias,
                                             self.config.font_fg_color)
            self.surface.blit(rendered_line, (position_x, position_y))
            position_y += self.text_y_offset


def print_loading_screen(config, surface):
    text = "LOADING..."
    text_font = create_font(config, 50)
    text_size = text_font.size(text)
    text_position = ((config.window_width/2)-(text_size[0]/2),
                     (config.window_height/2)-(text_size[1]/2))
    PrintText(config, surface, text_position, text_font)([text])
    pygame.display.flip()


def main():
    initialize_pygame_modules()
    display_info = get_display_info()
    config = command_line_args.parse_arguments(display_info)

    main_surface = create_main_surface(config)
    subsurfaces = create_sub_surfaces(config, main_surface)

    print_loading_screen(config, main_surface)

    channels = [
        RadiatorChannel(
            config=config,
            name="top",
            surface=subsurfaces[0],
            input_functor=AskTop(),
            output_functor=PrintText(config=config,
                                     surface=subsurfaces[0],
                                     position=(0, 0),
                                     font=create_font(config, 16)),
            update_period=5
        ),
        RadiatorChannel(
            config=config,
            name="cowsay",
            surface=subsurfaces[1],
            input_functor=AskTheCow(),
            output_functor=PrintText(config=config,
                                     surface=subsurfaces[1],
                                     position=(0, 0),
                                     font=create_font(config, 26)),
            update_period=10
        ),
        RadiatorChannel(
            config=config,
            name="w",
            surface=subsurfaces[2],
            input_functor=AskW(),
            output_functor=PrintText(config=config,
                                     surface=subsurfaces[2],
                                     position=(0, 0),
                                     font=create_font(config, 16)),
            update_period=15
        ),
        RadiatorChannel(
            config=config,
            name="finger",
            surface=subsurfaces[3],
            input_functor=AskFinger(),
            output_functor=PrintText(config=config,
                                     surface=subsurfaces[3],
                                     position=(0, 0),
                                     font=create_font(config, 16)),
            update_period=20
        )
    ]

    main_surface.fill(config.main_surface_color)

    for channel in channels:
        channel.turn_on()

    loop(config, subsurfaces, channels)

    for channel in channels:
        channel.turn_off()


sys.exit(main())
