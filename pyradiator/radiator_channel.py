import math
import random

import pygame

from common import create_font
from dispatcher import Dispatcher
from endpoint import Producer
from endpoint import Consumer


RRR = random.randrange


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


class RadiatorChannel(object):
    def __init__(self, args, surface, input_functor, output_functor, update_period):
        self.surface = surface
        self.static = create_static_surface(args, self.surface)
        self.overlay = create_no_signal_overlay(args)
        self.dispatcher = Dispatcher()
        self.producer = Producer(update_period,
                                 self.dispatcher.input_queue,
                                 input_functor)
        self.consumer = Consumer(math.ceil(update_period / 4),
                                 self.dispatcher.output_queue,
                                 output_functor)

    def turn_on(self):
        self.dispatcher.start()
        self.producer.start()
        self.consumer.start()

    def turn_off(self):
        self.consumer.stop()
        self.producer.stop()
        self.dispatcher.stop()

    def no_signal(self):
        return self.consumer.no_date_from_the_queue

    def display_static(self):
        x_offset = RRR(30) - 30
        y_offset = RRR(30) - 30
        self.static.scroll(x_offset, y_offset)
        self.surface.blit(self.static, (0, 0))
        self.surface.blit(self.overlay, (5, 5))
