"""
Common logging functionality to be used for multiple apps.
"""
import logging
import os


class OneLineExceptionFormatter(logging.Formatter):
    """
    Formatter used to insure each log-entry is one line.

    Insures one entry-per-log for some logging environments that divide
    on newline.
    """

    # pylint: disable=arguments-differ
    def formatException(self, exc_info):
        """Make sure exception-tracebacks end up on a single line."""

        result = super().formatException(exc_info)
        return repr(result)

    def format(self, record):
        """
        Convert newlines in each record to |
        """
        fmt_str = super().format(record)
        if record.exc_text:
            fmt_str = fmt_str.replace('\n', '') + '|'
        return fmt_str


def init_logging():
    """Setup root logger handler."""

    logger = logging.getLogger()
    handler = logging.StreamHandler()

    level = os.getenv('LOGGING_LEVEL_LIBS', "WARNING")
    logger.setLevel(getattr(logging, level, logging.WARNING))

    log_fmt = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"
    formatter = OneLineExceptionFormatter(log_fmt)

    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger(name):
    """
    Set logging level and return logger.

    Don't set custom logging level in root handler to not display debug
    messages from underlying libraries.
    """

    logger = logging.getLogger(name)
    level = os.getenv('LOGGING_LEVEL_APP', "INFO")
    logger.setLevel(getattr(logging, level, logging.INFO))
    return logger
