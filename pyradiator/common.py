import pygame


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
