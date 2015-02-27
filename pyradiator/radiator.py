import logging
import math
import subprocess
import sys
import os

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


def create_font(args, font_size=None):
    if args.font in pygame.font.get_fonts():
        return pygame.font.SysFont(args.font,
                                   font_size if font_size else args.font_size,
                                   args.font_bold,
                                   args.font_italic)
    else:
        return pygame.font.Font(args.font,
                                args.font_size)


def loop(args, subsurfaces):
    fps = 10
    display_refresh = pygame.USEREVENT
    pygame.time.set_timer(display_refresh, int(1000.0 / fps))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False
            elif event.type == display_refresh:
                pygame.display.flip()

        pygame.time.wait(0)


class AskTheCow(object):

    def __call__(self):
        proc1 = subprocess.Popen(["fortune", "-s"], stdout=subprocess.PIPE)
        proc2 = subprocess.Popen(["cowsay"], stdin=proc1.stdout,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc1.stdout.close()
        if PY3K:
            return proc2.communicate()[0].decode().split("\n")
        else:
            return proc2.communicate()[0].split("\n")


class AskTop(object):

    def __call__(self):
        proc = subprocess.Popen(["top", "-H", "-b", "-n1", "-p", str(os.getppid())],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if PY3K:
            return proc.communicate()[0].decode().split("\n")
        else:
            return proc.communicate()[0].split("\n")


class AskW(object):

    def __call__(self):
        proc = subprocess.Popen(["w", "-s"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if PY3K:
            return proc.communicate()[0].decode().split("\n")
        else:
            return proc.communicate()[0].split("\n")


class AskFinger(object):

    def __call__(self):
        proc = subprocess.Popen(["finger", os.getlogin()], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if PY3K:
            return proc.communicate()[0].decode().split("\n")
        else:
            return proc.communicate()[0].split("\n")


class PrintText(object):

    def __init__(self, args, surface, font_size=None):
        self.args = args
        self.surface = surface
        self.font = create_font(args, font_size)
        self.font_antialias = True
        self.text_y_offset = self.__get_text_y_offset(font_size)

    def __call__(self, lines_to_print):
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

    top_channel = RadiatorChannel(AskTop(), PrintText(args, subsurfaces[0], 16), 2)
    top_channel.turn_on()
    cow_channel = RadiatorChannel(AskTheCow(), PrintText(args, subsurfaces[1], 26), 40)
    cow_channel.turn_on()
    w_channel = RadiatorChannel(AskW(), PrintText(args, subsurfaces[2], 16), 2)
    w_channel.turn_on()
    finger_channel = RadiatorChannel(AskFinger(), PrintText(args, subsurfaces[3], 16), 10)
    finger_channel.turn_on()

    loop(args, subsurfaces)

    top_channel.turn_off()
    cow_channel.turn_off()
    w_channel.turn_off()
    finger_channel.turn_off()


sys.exit(main())
