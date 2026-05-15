import logging
import sys


def _build_logger() -> logging.Logger:
    logger = logging.getLogger("megumin")

    if logger.handlers:
        return logger  # evita adicionar handlers duplicados em reloads do uvicorn

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


logger = _build_logger()
