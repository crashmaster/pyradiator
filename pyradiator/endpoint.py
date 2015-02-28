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
        self.__thread.start()

    def stop(self):
        self._event.set()
        self.__thread.join()

    @abc.abstractmethod
    def _loop(self):
        pass


class Producer(Endpoint):

    def _loop(self):
#       self.__put_item_into_the_queue()
        while not self._event.wait(self._period_in_seconds):
            self.__put_item_into_the_queue()

    def __put_item_into_the_queue(self):
        try:
            self._queue.put((self._function, self._args))
        except queue.Full:
            pass


class Consumer(Endpoint):

    def __init__(self, period_in_seconds, queue, function, *args):
        super(Consumer, self).__init__(period_in_seconds, queue, function, *args)
        self.no_date_from_the_queue = True

    def _loop(self):
#       self.__get_item_out_of_the_queue()
        while not self._event.wait(self._period_in_seconds):
            self.__get_item_out_of_the_queue()

    def __get_item_out_of_the_queue(self):
        try:
            result = self._queue.get(block=False)
            self.no_date_from_the_queue = result is None
        except queue.Empty:
            return
        else:
            self._function(result, *self._args)
