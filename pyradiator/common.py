import getpass
import math

import pygame
import requests


def get_authenticator():
    user = input("User: ")
    password = getpass.getpass()
    return requests.auth.HTTPBasicAuth(user, password)


def create_font(config, font_size=None):
    if config.font in pygame.font.get_fonts():
        return pygame.font.SysFont(
            config.font,
            font_size if font_size else config.font_size,
            config.font_bold,
            config.font_italic
        )
    else:
        return pygame.font.Font(
            config.font,
            config.font_size
        )


class ColoredString(object):

    def __init__(self, text, color=(255, 255, 255)):
        self.text = text
        self.color = color

    def __str__(self):
        return "Text: {}, Color: {}".format(self.text, self.color)


class PrintText(object):

    def __init__(self, config, surface, position, font):
        self.config = config
        self.surface = surface
        self.position = position
        self.font = font
        self.text_y_offset = math.ceil(self.font.get_height() * 1.05)

    def __call__(self, lines_to_print):
        if not lines_to_print:
            return

        self.surface.fill(self.config.sub_surface_color)
        position_x = self.position[0]
        position_y = self.position[1]
        text_surface = self.surface.copy()
        for line in lines_to_print:
            for line_part in line:
                rendered_text = self.font.render(
                    line_part.text,
                    int(self.config.font_antialias),
                    line_part.color
                )
                text_surface.blit(rendered_text, (position_x, position_y))
                position_x += rendered_text.get_width()
            position_y += self.text_y_offset
            position_x = self.position[0]
        self.surface.blit(text_surface, (0, 0))


def print_loading_screen(config, surface):
    text = [[ColoredString("L", (0, 121, 234)),
             ColoredString("O", (23, 132, 234)),
             ColoredString("A", (47, 144, 234)),
             ColoredString("D", (70, 155, 234)),
             ColoredString("I", (94, 166, 234)),
             ColoredString("N", (117, 178, 234)),
             ColoredString("G", (140, 189, 234)),
             ColoredString(".", (164, 200, 234)),
             ColoredString(".", (187, 211, 234)),
             ColoredString(".", (211, 223, 234))]]
    text_font = create_font(config, int(math.ceil(config.window_height * 0.1)))
    text_size = text_font.size("".join(x.text for x in text[0]))
    text_position = ((config.window_width / 2) - (text_size[0] / 2),
                     (config.window_height / 2) - (text_size[1] / 2))
    PrintText(config, surface, text_position, text_font)(text)
    pygame.display.flip()
