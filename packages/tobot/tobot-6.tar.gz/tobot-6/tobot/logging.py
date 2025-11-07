# This file is placed in the Public Domain.


"logging"


import logging


LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}


class Logging:

    datefmt = "%H:%M:%S"
    format = "%(module).3s %(message)s"


class Formatter(logging.Formatter):

    def format(self, record):
        record.module = record.module.upper()
        return logging.Formatter.format(self, record)


def level(loglevel="debug"):
    if loglevel != "none":
        lvl = LEVELS.get(loglevel)
        if not lvl:
            return
        logger = logging.getLogger()
        for handler in logger.handlers:
            logger.removeHandler(handler)
        logger.setLevel(lvl)
        formatter = Formatter(Logging.format, datefmt=Logging.datefmt)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)


def __dir__():
    return (
        'level',
    )
