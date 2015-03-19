try:
    import queue
except ImportError:
    import Queue
import threading


class Producer(object):

    def __init__(self, period_in_seconds, queue, function):
        self._period_in_seconds = period_in_seconds
        self._queue = queue
        self._function = function
        self._event = threading.Event()
        self._thread = threading.Thread(target=self._loop)

    def start(self):
        self._thread.start()

    def stop(self):
        self._event.set()
        self._thread.join()

    def _loop(self):
        while not self._event.wait(self._period_in_seconds):
            self.__put_item_into_the_queue()

    def __put_item_into_the_queue(self):
        try:
            self._queue.put(self._function)
        except queue.Full:
            pass


class Consumer(object):

    STOP_SENTINEL = "STOP"

    def __init__(self, queue, function):
        self._queue = queue
        self._function = function
        self._thread = threading.Thread(target=self._loop)
        self.no_date_from_the_queue = True

    def start(self):
        self._thread.start()

    def stop(self):
        self._queue.put(self.STOP_SENTINEL)
        self._thread.join()

    def _loop(self):
        for result in iter(self._queue.get, self.STOP_SENTINEL):
            self.no_date_from_the_queue = result is None
            if result:
                self._function(result)
