import multiprocessing

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
