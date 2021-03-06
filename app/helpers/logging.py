import math
import urllib3
import logging
import datetime as dt

from helpers.singleton import singleton
from logging.handlers import WatchedFileHandler

@singleton
class Logging:
    logger = None

    current_step = None
    start_time = None
    total_steps = None
    desc = None
    verbosity = 0

    def __init__(self, logger_name):
        # disable HTTPS warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        logging.getLogger('urllib3').setLevel(logging.CRITICAL)

        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = False

    def add_stdout_handler(self):
        ch = logging.StreamHandler()
        ch.setLevel(self.logger.level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def add_file_handler(self, log_file):
        ch = WatchedFileHandler(log_file)
        ch.setLevel(self.logger.level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def init_ticker(self, total_steps=None, desc=None):
        """
        Initialize a ticker.
        Warning: this method is not independant. Call it only one at a time

        :param total_steps: number of total step
        :param desc: description of the ticker
        """
        self.total_steps = total_steps
        self.start_time = dt.datetime.today().timestamp()
        self.desc = desc
        self.current_step = 0

    def tick(self):
        """
        Increment the number of tick
        """
        self.current_step += 1

        if self.verbosity >= 5:
            should_log = True
        else:
            should_log = self.current_step % max(1, int(math.pow(10, (6 - self.verbosity)))) == 0 or \
                            self.current_step == self.total_steps

        if should_log:
            # avoid a division by zero
            time_diff = max(float(1), float(dt.datetime.today().timestamp() - self.start_time))
            ticks_per_second = "{:,}".format(round(float(self.current_step) / time_diff))

            self.logger.info(self.desc + " [" + ticks_per_second + " eps. - " + '{:.2f}'
                             .format(round(float(self.current_step) / float(self.total_steps) * 100, 2)) +
                             "% done" + "]")

    def print_generic_intro(self, title):
        """
        Display title in log

        :param title: title to display
        """
        self.logger.info("")
        self.logger.info("===== " + title + " =====")
