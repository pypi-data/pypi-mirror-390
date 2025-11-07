"""Logger c"""
import sys
import time
import logging
import traceback
import functools

class ColorFormatter(logging.Formatter):
    grey = "\x1b[38m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    blue = "\x1b[34m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(levelname)s - %(message)s"

    if sys.platform == "darwin":
        FORMATS = {
            logging.DEBUG: blue + format + reset,
            logging.INFO: grey + format + reset,
            logging.WARNING: yellow + format + reset,
            logging.ERROR: red + format + reset,
            logging.CRITICAL: bold_red + format + reset,
        }
    else:
        FORMATS = {
            logging.DEBUG: format,
            logging.INFO: format,
            logging.WARNING: format,
            logging.ERROR: format,
            logging.CRITICAL: format,
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class Logger:
    def __init__(self, log_file=None, log_level=logging.INFO):
        self.logger = logging.getLogger(__name__)
        if sys.platform == "darwin":
            log_level = logging.DEBUG
        self.logger.setLevel(log_level)

        formatter = ColorFormatter()
        if log_file is not None:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
        else:
            file_handler = logging.StreamHandler()
            file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

    def log(self, *args, sep=" ", log_level=logging.INFO):
        """Logs a message with the specified log level.
        Args:
            *args: Message to log
            sep (str, optional): Separator for args. Defaults to " ".
            log_level (int, optional): Log level. Defaults to logging.INFO.

        Example:

        >>> from utils.logging_utils import Logger
        >>> logger = Logger()
        >>> logger.log("Hello", "World")
        2021-05-26 15:00:00,000 - INFO - Hello World

        >>> logger.log("Hello", "World", log_level=logging.ERROR)
        2021-05-26 15:00:00,000 - ERROR - Hello World

        >>> logger.log("Hello", "World", sep="-")
        2021-05-26 15:00:00,000 - INFO - Hello-World
        """
        message = f"{sep.join([str(arg) for arg in args])}"
        self.logger.log(log_level, message)

    def log_func(
        self,
        log_inputs=True,
        log_outputs=True,
        max_input_length=200,
        max_output_length=200,
    ):
        """Decorator to log function calls and results.
        Args:
            log_inputs (bool, optional): Defines if the input should be logged. Defaults to True.
            log_outputs (bool, optional): Defines if the output should be logged. Defaults to True.

        Returns:
            function: Decorated function

        Example:

        >>> from utils.logging_utils import Logger
        >>> logger = Logger()
        >>>
        >>> @logger.log_func()
        >>> def hello_world(name):
        >>>     return f"Hello {name}"
        >>> hello_world("World")
        2021-05-26 15:00:00,000 - INFO - Entering Function hello_world called with args: ('World',), kwargs: {}.
        2021-05-26 15:00:00,000 - INFO - Exiting Function hello_world with result: Hello World and runtime: 0.0001
        """

        def decorator_log_func(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                if log_inputs:
                    args_str = f"{args}"[:max_input_length]
                    kwargs_str = f"{kwargs}"[:max_input_length]

                    self.log(
                        f"Entering Function {func.__name__} called with args: {args_str}, kwargs: {kwargs_str}. "
                    )
                else:
                    self.log(f"Entering Function {func.__name__}")
                try:
                    result = func(*args, **kwargs)
                    end_time = time.time()

                    runtime = end_time - start_time
                    if log_outputs:
                        result_str = f"{result}"[:max_output_length]
                        self.log(
                            f"Exiting Function {func.__name__} with result: {result_str} and runtime: {runtime}"
                        )
                    else:
                        self.log(
                            f"Exiting Function {func.__name__} with runtime: {runtime}"
                        )

                    return result
                except Exception as e:
                    self.logger.error(f"Error in Function {func.__name__}")
                    self.logger.error(traceback.format_exc())
                    raise e

            return wrapper

        return decorator_log_func

    def info(self, *args, **kwargs):
        self.log(*args, **kwargs, log_level=logging.INFO)

    def debug(self, *args, **kwargs):
        self.log(*args, **kwargs, log_level=logging.DEBUG)

    def warn(self, *args, **kwargs):
        self.log(*args, **kwargs, log_level=logging.WARNING)

    def warning(self, *args, **kwargs):
        self.log(*args, **kwargs, log_level=logging.WARNING)

    def error(self, *args, **kwargs):
        self.log(*args, **kwargs, log_level=logging.ERROR)

