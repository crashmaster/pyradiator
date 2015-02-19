import abc
import queue
import threading

import six


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
        six.print_("Start endpoint, period time: {}s.".
                   format(self._period_in_seconds))
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
