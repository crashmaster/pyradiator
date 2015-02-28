import pygame


def create_font(args, font_size=None):
    if args.font in pygame.font.get_fonts():
        return pygame.font.SysFont(args.font,
                                   font_size if font_size else args.font_size,
                                   args.font_bold,
                                   args.font_italic)
    else:
        return pygame.font.Font(args.font,
                                args.font_size)
