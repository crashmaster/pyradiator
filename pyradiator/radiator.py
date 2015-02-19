import logging
import sys

import pygame

FORMAT = "%(asctime)-15s %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
LOGGER = logging.getLogger("watrad")

WHITE = (255, 255, 255)
EDGE_OFFSET = 5


def initialize_pygame_modules():
    pygame.display.init()
    LOGGER.debug("pygame.display module initialized")
    pygame.font.init()
    LOGGER.debug("pygame.font module initialized")


def get_display_info():
    display_info = pygame.display.Info()
    LOGGER.debug("Display info: \n{}".format(display_info).rstrip())
    return display_info


def create_main_surface(display_info):
    resolution = (int(display_info.current_w / 2),
                  int(display_info.current_h / 2))
    flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    main_surface = pygame.display.set_mode(resolution, flags)
    LOGGER.debug("Main surface with resolution: {} created".format(resolution))
    return main_surface


def create_sub_surface(main_surface, x, y, width, height):
    sub_surface = main_surface.subsurface((x, y, width, height))
    LOGGER.debug("Sub surface with resolution: {} @ {} created".
                 format((width, height), (x, y)))
    return sub_surface


def create_sub_surfaces(display_info, main_surface):
    quarter_width = int(display_info.current_w / 4)
    quarter_height = int(display_info.current_h / 4)
    return [
        create_sub_surface(main_surface,
                           EDGE_OFFSET + i * quarter_width,
                           EDGE_OFFSET + j * quarter_height,
                           quarter_width - (2 * EDGE_OFFSET),
                           quarter_height - (2 * EDGE_OFFSET))
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
    main_surface = create_main_surface(display_info)
    create_sub_surfaces(display_info, main_surface)
    loop()

sys.exit(main())
