try:
    import queue
except ImportError:
    import Queue    # noqa
import threading


class Producer(object):

    def __init__(self, period_in_seconds, input_queue, input_functor):
        self._period_in_seconds = period_in_seconds
        self._input_queue = input_queue
        self._input_functor = input_functor
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
            self._input_queue.put(self._input_functor)
        except queue.Full:
            pass


class Consumer(object):

    STOP_SENTINEL = "STOP"

    def __init__(self, output_queue, output_functor):
        self._output_queue = output_queue
        self._output_functor = output_functor
        self._thread = threading.Thread(target=self._loop)
        self.no_data_from_the_queue = True
        self.request_update = False

    def start(self):
        self._thread.start()

    def stop(self):
        self._output_queue.put(self.STOP_SENTINEL)
        self._thread.join()

    def _loop(self):
        for result in iter(self._output_queue.get, self.STOP_SENTINEL):
            self.no_data_from_the_queue = not result
            if result:
                self._output_functor(result)
                self.request_update = True
