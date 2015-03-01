import math
import subprocess
import sys

import pygame


PY3K = sys.version_info >= (3, 0)


def _execute_command(function, *args, **kwargs):
    try:
        process = function(*args, **kwargs)
    except OSError:
        return
    else:
        if PY3K:
            return process.communicate()[0].decode().split("\n")
        else:
            return process.communicate()[0].split("\n")


def execute_simple_command(command):
    def _popen_call(command):
        process = subprocess.Popen(command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        return process

    return _execute_command(_popen_call, command)


def execute_compound_command(command_1, command_2):
    def _popen_calls(command_1, command_2):
        process_1 = subprocess.Popen(command_1,
                                     stdout=subprocess.PIPE)
        process_2 = subprocess.Popen(command_2,
                                     stdin=process_1.stdout,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        process_1.stdout.close()
        return process_2

    return _execute_command(_popen_calls, command_1, command_2)


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
        for line in lines_to_print:
            rendered_line = self.font.render(line,
                                             self.config.font_antialias,
                                             self.config.font_fg_color)
            self.surface.blit(rendered_line, (position_x, position_y))
            position_y += self.text_y_offset


def print_loading_screen(config, surface):
    text = "LOADING..."
    text_font = create_font(config, math.ceil(config.window_height*0.1))
    text_size = text_font.size(text)
    text_position = ((config.window_width/2)-(text_size[0]/2),
                     (config.window_height/2)-(text_size[1]/2))
    PrintText(config, surface, text_position, text_font)([text])
    pygame.display.flip()
