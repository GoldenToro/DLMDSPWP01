import logging

logging_level = logging.DEBUG

class ColorFormatter(logging.Formatter):
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


logger = logging.getLogger("DLMDSPWP01")
logger.setLevel(logging_level)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging_level)
ch.setFormatter(ColorFormatter())

logger.addHandler(ch)

