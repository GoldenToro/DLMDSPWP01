import logging

LOGGING_LEVEL = logging.INFO


class LoggingLevelError(Exception):
    """
    Exception raised for errors in the logging level.

    :param message: Explanation of the error.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ColorFormatter(logging.Formatter):
    """
    Custom formatter to add color to logging messages.
    """
    green = "\x1b[1;32m"
    grey = "\x1b[1;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger:
    """
    Logger setup and configuration.

    :param name: Name of the logger.
    :param level: Logging level.
    :raises LoggingLevelError: If the logging level is not an integer.
    """

    def __init__(self, name: str, level: int):
        self.logger = logging.getLogger(name)
        try:
            if not isinstance(level, int):
                raise LoggingLevelError("Logging level must be an integer.")
            self.logger.setLevel(level)
        except LoggingLevelError as e:
            print(e)
            level = logging.DEBUG
            self.logger.setLevel(level)
        self.set_handler(level)

    def set_handler(self, level: int):
        """
        Set the handler for the logger.

        :param level: Logging level for the handler.
        """
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(ColorFormatter())
        self.logger.addHandler(ch)


logger = Logger("DLMDSPWP01", LOGGING_LEVEL).logger
logger.info("Logger initialized successfully.")
