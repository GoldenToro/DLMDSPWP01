import logging

class ColorFormatter(logging.Formatter):

    green = "\x1b[1;32m"
    grey = "\x1b[1;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s (%(filename)s:%(lineno)d)\t- %(levelname)s\t- %(message)s "

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


def create_logger(name="no-name",level="DEBUG"):

    log_level = logging.DEBUG

    if level == "INFO":
        log_level = logging.INFO

    # create logger with 'spam_application'
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(level)

    ch.setFormatter(ColorFormatter())

    logger.addHandler(ch)

    return logger
