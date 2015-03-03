import multiprocessing


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

    def __worker(self):
        for function in iter(self.input_queue.get, self.STOP_SENTINEL):
            result = function()
            self.output_queue.put(result)
