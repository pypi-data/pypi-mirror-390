import logging

logger_name = __name__.split(".")[0]
# Create a logger specific to your library
logger = logging.getLogger(logger_name)
logger.addHandler(logging.NullHandler())

def enable_default_logging(level=logging.INFO):
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)