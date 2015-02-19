import abc
import queue
from random import randrange
from datetime import datetime
from multiprocessing import Process
from multiprocessing import Queue
from threading import Event
from threading import Thread
from threading import Timer

import six


def mul(a, b):
    return "@{} -> {} * {} = {}".format(datetime.now(), a, b, a * b)


def print_tabbed(string):
    six.print_("\t{}.".format(string))


class Dispatcher(object):

    STOP_SENTINEL = "STOP"

    def __init__(self):
        self.input_queue = Queue()
        self.output_queue = Queue()
        self.__process = Process(target=self.__worker)

    def start(self):
        self.__process.start()

    def stop(self):
        self.input_queue.put(self.STOP_SENTINEL)
        self.input_queue.close()
        self.output_queue.close()
        self.__process.join()
        self.__process.terminate()
        six.print_("Stop process.")

    def __worker(self):
        six.print_("Start worker.")
        for function, args in iter(self.input_queue.get, self.STOP_SENTINEL):
            result = function(*args)
            self.output_queue.put(result)
        six.print_("Stop worker.")


@six.add_metaclass(abc.ABCMeta)
class Endpoint(object):

    def __init__(self, period_in_seconds, queue, function, *args):
        self._period_in_seconds = period_in_seconds
        self._queue = queue
        self._function = function
        self._args = args
        self._event = Event()
        self.__thread = Thread(target=self._loop)

    def start(self):
        six.print_("Start endpoint, period time: {}s.".format(self._period_in_seconds))
        self.__thread.start()

    def stop(self):
        six.print_("Stop endpoint.")
        self._event.set()
        self.__thread.join()

    @abc.abstractmethod
    def _loop(self):
        pass


class Producer(Endpoint):

    def _loop(self):
        while not self._event.wait(self._period_in_seconds):
            try:
                self._queue.put((self._function, self._args))
            except queue.Full:
                pass


class Consumer(Endpoint):

    def _loop(self):
        while not self._event.wait(self._period_in_seconds):
            try:
                result = self._queue.get()
            except queue.Empty:
                continue
            else:
                self._function(result, *self._args)


def main():
    dispatcher = Dispatcher()
    dispatcher.start()
    producer = Producer(2, dispatcher.input_queue, mul, randrange(3, 6), randrange(7, 12))
    producer.start()
    consumer = Consumer(1, dispatcher.output_queue, print_tabbed)
    consumer.start()

    def stop_stuff():
        consumer.stop()
        producer.stop()
        dispatcher.stop()

    Timer(9, stop_stuff).start()

if __name__ == "__main__":
    rr = randrange(2, 15)
    six.print_("{}{} Starting {} test objects {}{}".format("-" * 16, ">>>", rr, "<<<", "-" * 16))
    for i in range(rr):
        main()
