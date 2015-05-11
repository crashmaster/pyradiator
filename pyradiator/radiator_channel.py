import random

import pygame

from pyradiator.common import create_font
from pyradiator.dispatcher import Dispatcher
from pyradiator.endpoint import Consumer
from pyradiator.endpoint import Producer


RRR = random.randrange


def create_static_surface(config, surface):
    (width, height) = surface.get_size()
    static_width = width + 60
    static_height = height + 60
    static = pygame.Surface((static_width, static_height))
    colors = (
        static.map_rgb(config.static_bg_color),
        static.map_rgb(config.static_fg_color)
    )
    random_choice = random.choice
    set_pixel_color_at = static.set_at
    y_range = range(static_height)
    for x in range(static_width):
        for y in y_range:
            set_pixel_color_at((x, y), random_choice(colors))
    return static


def create_no_signal_overlay(config, channel_name):
    font = create_font(config, 24)
    text = "Channel '{}': {}.".format(channel_name, "No signal")
    no_signal = font.render(text, 1, config.font_fg_color)
    overlay = pygame.Surface(tuple(x + 5 for x in font.size(text)), pygame.SRCALPHA)
    overlay.fill((30, 30, 30, 200))
    overlay.blit(no_signal, (5, 0))
    return overlay


class RadiatorChannel(object):
    def __init__(self, config, name, surface, input_functor, output_functor, update_period):
        self.config = config
        self.surface = surface
        self.static = create_static_surface(self.config, self.surface)
        self.overlay = create_no_signal_overlay(self.config, name)
        self.dispatcher = Dispatcher()
        self.producer = Producer(update_period,
                                 self.dispatcher.input_queue,
                                 input_functor)
        self.consumer = Consumer(self.dispatcher.output_queue,
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
        return self.consumer.no_data_from_the_queue

    def display_static(self, clock):
        x_offset = RRR(30) - 30
        y_offset = RRR(30) - 30
        self.static.scroll(x_offset, y_offset)
        self.surface.blit(self.static, (0, 0))
        self.surface.blit(self.overlay, (5, 5))
        if not pygame.event.peek(pygame.USEREVENT):
            pygame.event.post(pygame.event.Event(pygame.USEREVENT))
        clock.tick(self.config.fps)
