import math

from dispatcher import Dispatcher
from endpoint import Producer
from endpoint import Consumer


class RadiatorChannel(object):
    def __init__(self, input_functor, output_functor, update_period):
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
