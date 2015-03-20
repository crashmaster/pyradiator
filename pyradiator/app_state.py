import contextlib
import logging
import signal
import sys


LOGGER = logging.getLogger(__name__)


class ApplicationState(object):

    LOAD = 0
    MAIN_LOOP = 1

    def __init__(self):
        self.state = self.LOAD
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)

    def set_application_state(self, state):
        self.state = state

    def stop_main_loop(self):
        self.running = False

    def signal_handler(self, signal, frame):
        if self.state == self.LOAD:
            self._handle_signal_in_load_state()
        elif self.state == self.MAIN_LOOP:
            self._handle_signal_in_main_loop_state()
        else:
            raise RuntimeError("Invalid application state: {}".format(self.state))

    @contextlib.contextmanager
    def suspend_signal_handling(self):
        current_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        yield
        signal.signal(signal.SIGINT, current_handler)

    def _handle_signal_in_load_state(self):
        LOGGER.debug("Handle SIGINT in 'load' state, do exit")
        sys.exit(1)

    def _handle_signal_in_main_loop_state(self):
        LOGGER.debug("Handle SIGINT in 'main loop' state, stop the main loop")
        self.stop_main_loop()
