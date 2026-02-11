import logging
import sys


def configure_app_logging() -> None:
    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    for name in ("main", "security.signature"):
        log = logging.getLogger(name)
        log.setLevel(logging.INFO)
        log.propagate = False
        log.addHandler(handler)
