import abc
import multiprocessing
import queue
import threading

import six


class Dispatcher(object):

    STOP_SENTINEL = "STOP"

    def __init__(self):
        self.input_queue = multiprocessing.Queue()
        self.output_queue = multiprocessing.Queue()
        self.__process = multiprocessing.Process(target=self.__worker)

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
        self._event = threading.Event()
        self.__thread = threading.Thread(target=self._loop)

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
