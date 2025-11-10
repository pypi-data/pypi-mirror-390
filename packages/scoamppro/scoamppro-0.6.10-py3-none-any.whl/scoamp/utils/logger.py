import logging
from rich.logging import RichHandler

lib_name = __name__.split(".")[0]


def get_logger(name: str = None):
    if name is None:
        name = lib_name
    return logging.getLogger(name)


def _init_logger():
    logger = get_logger()
    handler = RichHandler(
        rich_tracebacks=True, omit_repeated_times=False, show_path=False
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


_init_logger()
del _init_logger
