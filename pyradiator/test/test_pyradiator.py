from datetime import datetime
from random import randrange
from threading import Timer

from pyradiator.dispatcher import Dispatcher
from pyradiator.endpoint import Consumer
from pyradiator.endpoint import Producer


PRODUCER_WAKE_UP_TIME = 2


class Multiply(object):

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __call__(self):
        return "@{} -> {} * {} = {}".format(datetime.now(),
                                            self.a,
                                            self.b,
                                            self.a * self.b)


def print_tabbed(string):
    print("\t{}.".format(string))


def main():
    dispatcher = Dispatcher()
    producer = Producer(PRODUCER_WAKE_UP_TIME,
                        dispatcher.input_queue,
                        Multiply(randrange(3, 6), randrange(7, 12)))
    consumer = Consumer(dispatcher.output_queue,
                        print_tabbed)

    def start_stuff():
        dispatcher.start()
        producer.start()
        consumer.start()

    def stop_stuff():
        consumer.stop()
        producer.stop()
        dispatcher.stop()

    start_stuff()
    Timer(9, stop_stuff).start()


if __name__ == "__main__":
    print("{}{} Starting {} test objects {}{}".
          format("-" * 16, ">>>", randrange(2, 6), "<<<", "-" * 16))
    for i in range(randrange(2, 6)):
        main()
