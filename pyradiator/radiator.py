import logging
import math
import os
import random
import subprocess
import sys

import pygame

import command_line_args
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


def create_main_surface(args):
    pygame.display.set_caption("PyRadiator by Crashmaster")
    resolution = (args.window_width, args.window_height)
    flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    if args.fullscreen:
        flags |= pygame.FULLSCREEN
        LOGGER.debug("Fullscreen mode enabled")
    main_surface = pygame.display.set_mode(resolution, flags)
    main_surface.fill(args.main_surface_color)
    LOGGER.debug("Main surface with resolution: {} created".
                 format(resolution))
    return main_surface


def create_sub_surface(args, main_surface, x, y, width, height):
    sub_surface = main_surface.subsurface((x, y, width, height))
    sub_surface.fill(args.sub_surface_color)
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


def create_static_surface(args, surface):
    (width, height) = surface.get_size()
    static_width = width + 60
    static_height = height + 60
    static = pygame.Surface((static_width, static_height))
    colors = static.map_rgb(args.font_bg_color), static.map_rgb(args.font_fg_color)
    random_choice = random.choice
    set_pixel_color_at = static.set_at
    y_range = range(static_height)
    for x in range(static_width):
        for y in y_range:
            set_pixel_color_at((x, y), random_choice(colors))
    return static


def create_no_signal_overlay(args):
    font = create_font(args, 24)
    text = "No Signal."
    no_signal = font.render(text, 1, args.font_fg_color)
    overlay = pygame.Surface(tuple(x + 5 for x in font.size(text)), pygame.SRCALPHA)
    overlay.fill((30, 30, 30, 200))
    overlay.blit(no_signal, (5, 0))
    return overlay


def create_font(args, font_size=None):
    if args.font in pygame.font.get_fonts():
        return pygame.font.SysFont(args.font,
                                   font_size if font_size else args.font_size,
                                   args.font_bold,
                                   args.font_italic)
    else:
        return pygame.font.Font(args.font,
                                args.font_size)


def loop(args, subsurfaces, static, overlay):
    fps = 50
    display_refresh = pygame.USEREVENT
    pygame.time.set_timer(display_refresh, int(1000.0 / fps))
    rrr = random.randrange
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False
            elif event.type == display_refresh:
                pygame.display.flip()
            x_offset = rrr(30) - 30
            y_offset = rrr(30) - 30
            static.scroll(x_offset, y_offset)
            subsurfaces[3].blit(static, (0, 0))
            subsurfaces[3].blit(overlay, (5, 5))

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
    process_1 = subprocess.Popen(command_1, stdout=subprocess.PIPE)
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
        return execute_compound_command(["fortune", "-s"], ["cowsay", random.choice(self.cows)])


class AskTop(object):

    def __call__(self):
        return execute_simple_command(["top", "-H", "-b", "-n1", "-p", str(os.getppid())])


class AskW(object):

    def __call__(self):
        return execute_simple_command(["w", "-s"])


class AskFinger(object):

    def __call__(self):
        return execute_simple_command(["finger", os.getlogin()])


class PrintText(object):

    def __init__(self, args, surface, font_size=None):
        self.args = args
        self.surface = surface
        self.font = create_font(args, font_size)
        self.font_antialias = True
        self.text_y_offset = self.__get_text_y_offset(font_size)

    def __call__(self, lines_to_print):
        if not lines_to_print:
            return

        self.surface.fill(self.args.sub_surface_color)
        offset = 0
        for line in lines_to_print:
            rendered_line = self.font.render(line,
                                             self.font_antialias,
                                             self.args.font_fg_color,
                                             self.args.font_bg_color)
            self.surface.blit(rendered_line, (0, offset))
            offset += self.text_y_offset

    def __get_text_y_offset(self, font_size):
        return math.ceil((font_size if font_size else self.args.font_size) * 1.25)


def main():
    initialize_pygame_modules()
    display_info = get_display_info()
    args = command_line_args.parse_arguments(display_info)

    main_surface = create_main_surface(args)
    subsurfaces = create_sub_surfaces(args, main_surface)
    static = create_static_surface(args, subsurfaces[3])
    overlay = create_no_signal_overlay(args)

    top_channel = RadiatorChannel(AskTop(), PrintText(args, subsurfaces[0], 16), 2)
    top_channel.turn_on()
    cow_channel = RadiatorChannel(AskTheCow(), PrintText(args, subsurfaces[1], 26), 10)
    cow_channel.turn_on()
    w_channel = RadiatorChannel(AskW(), PrintText(args, subsurfaces[2], 16), 2)
    w_channel.turn_on()
#   finger_channel = RadiatorChannel(AskFinger(), PrintText(args, subsurfaces[3], 16), 10)
#   finger_channel.turn_on()

    loop(args, subsurfaces, static, overlay)

    top_channel.turn_off()
    cow_channel.turn_off()
    w_channel.turn_off()
#   finger_channel.turn_off()


sys.exit(main())
