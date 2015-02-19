from datetime import datetime
from random import randrange
from threading import Timer

from dispatcher import Dispatcher
from endpoint import Consumer
from endpoint import Producer


PRODUCER_WAKE_UP_TIME = 2
CONSUMER_WAKE_UP_TIME = PRODUCER_WAKE_UP_TIME / 2


def multiply(a, b):
    return "@{} -> {} * {} = {}".format(datetime.now(), a, b, a * b)


def print_tabbed(string):
    print("\t{}.".format(string))


def main():
    dispatcher = Dispatcher()
    producer = Producer(PRODUCER_WAKE_UP_TIME,
                        dispatcher.input_queue,
                        multiply,
                        randrange(3, 6),
                        randrange(7, 12))
    consumer = Consumer(CONSUMER_WAKE_UP_TIME,
                        dispatcher.output_queue,
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
