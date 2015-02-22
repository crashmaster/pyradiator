import datetime
import logging
import sys

import pygame

import command_line_args

IS_HELP_MODE = any(x in sys.argv for x in ["-h", "--help", "list"])
LOG_LEVEL = logging.ERROR if IS_HELP_MODE else logging.DEBUG
FORMAT = "%(asctime)-15s %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=LOG_LEVEL)

LOGGER = logging.getLogger("watrad")


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


def create_font(args):
    if args.font in pygame.font.get_fonts():
        return pygame.font.SysFont(args.font,
                                   args.font_size,
                                   args.font_bold,
                                   args.font_italic)
    else:
        return pygame.font.Font(args.font,
                                args.font_size)


def loop(args, subsurfaces, font):
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

        for subsurface in subsurfaces:
            subsurface.fill(args.sub_surface_color)
            time = font.render(str(datetime.datetime.now()),
                               True,
                               args.font_fg_color,
                               args.font_bg_color)
            subsurface.blit(time, (0, 0))

        pygame.time.wait(0)


def main():
    initialize_pygame_modules()
    display_info = get_display_info()
    args = command_line_args.parse_arguments(display_info)
    main_surface = create_main_surface(args)
    subsurfaces = create_sub_surfaces(args, main_surface)
    font = create_font(args)
    loop(args, subsurfaces, font)

sys.exit(main())
