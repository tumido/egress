"""
Common logging functionality to be used for multiple apps.
"""
import logging
import os
from logstash_formatter import LogstashFormatterV1


def init_logging():
    """Setup default logging configuration."""
    handler = logging.StreamHandler()
    handler.setFormatter(LogstashFormatterV1())

    level = os.getenv('LOGGING_LEVEL_LIBS', 'INFO')
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level))
